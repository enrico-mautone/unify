from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path

# Directory base
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Configurazione database
    DATABASE_URL: str = Field(default=f"sqlite:///{BASE_DIR}/auth.db", env="DATABASE_URL")
    
    # Configurazione JWT
    SECRET_KEY: str = Field(default="your-secret-key-change-this-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Configurazione password hashing
    PWD_CONTEXT_SCHEMES: list = Field(default=["bcrypt"], env="PWD_CONTEXT_SCHEMES")
    PWD_CONTEXT_DEPRECATED: str = Field(default="auto", env="PWD_CONTEXT_DEPRECATED")
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

# Crea un'istanza delle impostazioni
settings = Settings()
