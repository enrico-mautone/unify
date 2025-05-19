from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

from app import models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token, TokenPayload
from app.schemas.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
@router.options("/login", include_in_schema=False)
async def login_access_token(
    request: Request,
    response: Response,
    login_data: dict = None,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Log della richiesta
    print(f"\n=== Nuova richiesta di login ===")
    print(f"Metodo: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Client: {request.client}")
    
    # Gestisci la richiesta OPTIONS per CORS preflight
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.status_code = 200
        return response
    
    # Leggi il corpo della richiesta grezzo
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        print(f"Corpo della richiesta grezzo: {body_str}")
        
        # Se non abbiamo ancora i dati del login, proviamo a leggerli dal corpo JSON
        if not login_data and body_str:
            try:
                login_data = await request.json()
                print(f"Dati del login dal JSON: {login_data}")
            except Exception as e:
                print(f"Errore nel parsing del JSON: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Formato della richiesta non valido. Atteso un oggetto JSON con 'username' e 'password'"
                )
    except Exception as e:
        print(f"Errore nella lettura del corpo della richiesta: {str(e)}")
    
    # Verifica che i dati del login siano presenti
    if not login_data or 'password' not in login_data or ('username' not in login_data and 'email' not in login_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/username e password sono richiesti"
        )
    
    # Supporta sia 'username' che 'email' come chiave
    username = login_data.get('username', login_data.get('email'))
    password = login_data['password']
    
    print(f"Tentativo di login con email/username: {username}")
    
    # Verifica le credenziali hardcoded
    if username != "super.unify@purpleswan.com" or password != "password01!":
        print("Credenziali non valide")
        response.headers["Access-Control-Allow-Origin"] = "*"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print("Credenziali valide, generazione token...")
    
    # Aggiungi header CORS alla risposta
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    # Crea un utente fittizio per il test
    user = schemas.User(
        id=1,
        email="super.unify@purpleswan.com",
        full_name="Super Admin",
        is_active=True,
        is_superuser=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    # Crea il token di accesso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "is_superuser": user.is_superuser},
        expires_delta=access_token_expires
    )
    
    print(f"Token generato con successo per l'utente: {user.email}")
    
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser
        }
    }

@router.get("/test-token", response_model=User)
async def test_token(current_user: User = Depends(deps.get_current_user)):
    """
    Test access token
    """
    return current_user

@router.post("/logout")
async def logout():
    """
    Logout - Invalida il token corrente
    """
    # In un'implementazione reale, qui potresti invalidare il token
    return {"message": "Successfully logged out"}
