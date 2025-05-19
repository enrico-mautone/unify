# Importa qui tutti i modelli per renderli disponibili in un unico import
from .base import BaseModel
from .user import User

# Questo assicura che i modelli vengano rilevati da SQLAlchemy per la creazione delle tabelle
__all__ = ["BaseModel", "User"]
