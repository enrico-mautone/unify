from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    """Schema per il token di accesso"""
    access_token: str = Field(..., description="Token di accesso JWT")
    token_type: str = Field("bearer", description="Tipo di token, di solito 'bearer'")

class TokenPayload(BaseModel):
    """Schema per il payload del token JWT"""
    sub: Optional[int] = None  # Subject (user id)
    email: Optional[str] = None
    is_superuser: bool = False
