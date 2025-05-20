from sqlalchemy import Boolean, Column, Integer, String
from .database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

# Modelli Pydantic per la validazione
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
