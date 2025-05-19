from typing import Optional, AsyncGenerator, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_token
from app.db.session import async_session, get_db
from app.schemas.user import TokenData, User

# Schema per l'autenticazione OAuth2 con password flow
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    """Dipendenza per ottenere l'utente corrente autenticato"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    print(f"Token ricevuto: {token}")
    
    try:
        payload = verify_token(token)
        if payload is None:
            print("Token non valido: payload vuoto")
            raise credentials_exception
        
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        is_superuser: bool = payload.get("is_superuser", False)
        
        print(f"Dati estratti dal token - Email: {email}, User ID: {user_id}, Superuser: {is_superuser}")
        
        if email is None or user_id is None:
            print("Email o user_id mancanti nel token")
            raise credentials_exception
        
        token_data = TokenData(email=email)
        
        # Qui dovresti implementare la logica per ottenere l'utente dal database
        # user = await crud.user.get_by_email(db, email=token_data.email)
        # if user is None:
        #     raise credentials_exception
        # return user
        
        # Per ora restituiamo un utente fittizio basato sui dati del token
        return User(
            id=int(user_id) if user_id else 1,
            email=email,
            full_name="Admin User",
            is_active=True,
            is_superuser=is_superuser,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    except (JWTError, ValidationError) as e:
        print(f"Errore durante la validazione del token: {str(e)}")
        raise credentials_exception


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dipendenza per verificare se l'utente è un superutente"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
