from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer, DateTime, func
from datetime import datetime
from app.db.session import Base

class BaseModel(Base):
    """Classe base per tutti i modelli con colonne comuni"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @declared_attr
    def __tablename__(cls):
        """Genera automaticamente il nome della tabella dal nome della classe"""
        return cls.__name__.lower()
