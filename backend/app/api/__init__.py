from fastapi import APIRouter

# Importa qui i router delle singole risorse
from .v1 import api_router as v1_router

api_router = APIRouter()

# Includi il router della versione 1 dell'API
api_router.include_router(v1_router, prefix="/v1")
