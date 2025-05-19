# Importa qui tutti gli schemi per renderli disponibili in un unico import
from .user import User, UserCreate, UserInDB, UserUpdate, TokenData
from .token import Token, TokenPayload

# Questo assicura che gli schemi siano disponibili per l'importazione
__all__ = [
    "User", "UserCreate", "UserInDB", "UserUpdate", "TokenData",
    "Token", "TokenPayload"
]
