from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.db.session import engine, Base
from app.api import api_router

# Importa i modelli per assicurarti che vengano registrati con SQLAlchemy
from app.models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creazione delle tabelle del database all'avvio
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Qui puoi aggiungere codice di inizializzazione
    print("\n=== Avvio dell'applicazione ===")
    print(f"Ambiente: {settings.ENV}")
    print(f"Database: {settings.DATABASE_URL}")
    
    yield
    
    # Pulizia alla chiusura
    await engine.dispose()
    print("\n=== Chiusura dell'applicazione ===")

# Crea l'applicazione FastAPI
app = FastAPI(
    title="Shoe Production Manager API",
    description="API per la gestione della produzione di scarpe",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Per ora permettiamo tutte le origini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # 10 minuti di cache per le richieste preflight
)

# Aggiungi header CORS manualmente per le richieste OPTIONS
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, DELETE, PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.status_code = 200
    return response

# Includi i router API
app.include_router(api_router, prefix=settings.API_V_STR)

@app.get("/")
async def root():
    return {
        "message": "Benvenuto nell'API di gestione produzione scarpe",
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )
