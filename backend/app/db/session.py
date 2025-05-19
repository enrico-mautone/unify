from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSessionType
from typing import AsyncGenerator
from ..core.config import settings

# Crea il motore del database asincrono
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True,  # Impostare su False in produzione
    future=True
)

# Crea una factory di sessioni asincrone
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Crea una sessione sincrona per le operazioni che non supportano asincrono
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine.sync_engine if hasattr(engine, 'sync_engine') else None,
    class_=AsyncSession
)

# Base per i modelli
Base = declarative_base()

# Dipendenza per ottenere la sessione del database in modo asincrono
async def get_db() -> AsyncGenerator[AsyncSessionType, None]:
    """Dipendenza per ottenere una sessione del database"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
