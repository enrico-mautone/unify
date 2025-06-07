import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Percorso assoluto del database
BASE_DIR = Path(__file__).parent
SQLITE_DB_PATH = str(BASE_DIR / "entity.db")

# Carica le variabili d'ambiente dal file .env
load_dotenv()

class Settings:
    # Configurazione del server
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8081"))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Configurazione del database principale (per le entità)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "unify_admin")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password01!")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "unify_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Configurazione del database dell'applicazione
    APP_DB_USER: str = os.getenv("APP_DB_USER", "unify_admin")
    APP_DB_PASSWORD: str = os.getenv("APP_DB_PASSWORD", "password01!")
    APP_DB_NAME: str = os.getenv("APP_DB_NAME", "unify_db")
    APP_DB_HOST: str = os.getenv("APP_DB_HOST", "localhost")
    APP_DB_PORT: str = os.getenv("APP_DB_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        """Costruisce l'URL di connessione al database delle entità."""
        return f"sqlite:///{SQLITE_DB_PATH}"
        return "sqlite:///./entity.db"
        
    @property
    def APP_DATABASE_URL(self) -> str:
        """Costruisce l'URL di connessione al database dell'applicazione."""
        return "sqlite:///./app.db"
    
    @property
    def TEST_DATABASE_URL(self) -> str:
        """URL di test per il database."""
        return os.getenv(
            "TEST_DATABASE_URL",
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/test_{self.POSTGRES_DB}"
        )
    
    # Configurazione CORS
    @property
    def CORS_ORIGINS(self) -> list:
        """Lista delle origini CORS consentite."""
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        return [origin.strip() for origin in cors_origins.split(",")] if cors_origins != "*" else ["*"]
    
    # Configurazione autenticazione
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Ambiente (development, testing, production)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    
    @property
    def is_production(self) -> bool:
        """Restituisce True se l'ambiente è di produzione."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Restituisce True se l'ambiente è di sviluppo."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_testing(self) -> bool:
        """Restituisce True se l'ambiente è di test."""
        return self.ENVIRONMENT == "testing"

# Crea un'istanza delle impostazioni
settings = Settings()

# Crea le directory necessarie se non esistono
os.makedirs(Path("logs"), exist_ok=True)
os.makedirs(Path("data"), exist_ok=True)
