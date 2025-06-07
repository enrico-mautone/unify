from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, JSON, DateTime, text, Float, Boolean
from sqlalchemy.orm import sessionmaker, validates
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from pydantic import BaseModel as PydanticBaseModel
import json
import logging

# Configura il logger
logger = logging.getLogger(__name__)
from passlib.context import CryptContext
from pydantic import BaseModel, Field, EmailStr, field_validator, FieldValidationInfo
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, Index, func, DateTime, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import text
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
import logging

# Configura il logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler per la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Importa le impostazioni
from config import settings

# Configurazione del database PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica la connessione prima di ogni esecuzione
    pool_size=5,         # Dimensione del pool di connessioni
    max_overflow=10,     # Numero massimo di connessioni oltre al pool
    pool_recycle=3600    # Ricicla le connessioni dopo 1 ora
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelli del database
class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # Rimosso unique per permettere omonimi in rami diversi
    table_name = Column(String, unique=True, index=True, nullable=False)
    is_field = Column(Boolean, default=False, nullable=False)
    field_type = Column(String, nullable=True)  # Aggiunto per memorizzare il tipo di campo
    required = Column(Boolean, default=True)  # Aggiunto per memorizzare se il campo è obbligatorio
    default_value = Column(String, nullable=True)  # Aggiunto per memorizzare il valore di default
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent_id = Column(Integer, ForeignKey('entities.id'), nullable=True)
    
    # Relationships
    parent = relationship("Entity", remote_side=[id], backref="children")
    
    # Add validation to prevent circular references
    @validates('parent_id')
    def validate_parent_id(self, key, parent_id):
        if parent_id == self.id:
            raise ValueError("An entity cannot be its own parent")
        return parent_id
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', table_name='{self.table_name}')>"

# Rimossa la classe EntityField in favore dell'approccio con is_field
    
    # Add validation to prevent self-reference
    @validates('field_entity_id')
    def validate_field_entity_id(self, key, field_entity_id):
        if field_entity_id == self.entity_id:
            raise ValueError("A field cannot reference its own entity")
        return field_entity_id
    
    def __repr__(self):
        return f"<EntityField(id={self.id}, field_name='{self.field_name}', field_type='{self.field_type}')>"

# Aggiungi un listener per il log degli eventi dell'oggetto Entity
@event.listens_for(Entity, 'before_insert')
def log_before_insert(mapper, connection, target):
    logger.info("\n" + "="*50)
    logger.info("TENTATIVO DI CREAZIONE NUOVA ENTITÀ")
    logger.info(f"Nome: {target.name}")
    logger.info(f"Tabella: {target.table_name}")
    logger.info("Campi:")
    
    if isinstance(target.fields, dict):
        for field_name, field_data in target.fields.items():
            logger.info(f"  - {field_name}: {field_data.get('type', 'string')} "
                      f"(obbligatorio: {field_data.get('required', False)}, "
                      f"default: {field_data.get('default', 'Nessuno')})")
    elif isinstance(target.fields, list):
        for field in target.fields:
            if isinstance(field, dict):
                logger.info(f"  - {field.get('name', 'Sconosciuto')}: {field.get('type', 'string')} "
                          f"(obbligatorio: {field.get('required', False)}, "
                          f"default: {field.get('default', 'Nessuno')})")
    
    logger.info("="*50 + "\n")

@event.listens_for(Entity, 'before_update')
def log_before_update(mapper, connection, target):
    logger.info("\n" + "="*50)
    logger.info(f"AGGIORNAMENTO ENTITÀ: {target.name} (ID: {target.id})")
    logger.info("Nuovi campi:")
    
    if isinstance(target.fields, dict):
        for field_name, field_data in target.fields.items():
            logger.info(f"  - {field_name}: {field_data.get('type', 'string')} "
                      f"(obbligatorio: {field_data.get('required', False)}, "
                      f"default: {field_data.get('default', 'Nessuno')})")
    elif isinstance(target.fields, list):
        for field in target.fields:
            if isinstance(field, dict):
                logger.info(f"  - {field.get('name', 'Sconosciuto')}: {field.get('type', 'string')} "
                          f"(obbligatorio: {field.get('required', False)}, "
                          f"default: {field.get('default', 'Nessuno')})")
    
    logger.info("="*50 + "\n")

# Crea le tabelle
Base.metadata.create_all(bind=engine)

# Modelli Pydantic
class FieldType(str):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"

class FieldDefinition(BaseModel):
    name: str
    type: str
    required: bool = True
    default: Optional[str] = None

class EntityFieldCreate(BaseModel):
    field_name: str
    field_entity_id: int
    field_type: str
    required: bool = True
    default_value: Optional[str] = None

class EntityCreate(BaseModel):
    name: str
    table_name: str
    fields: List[EntityFieldCreate]
    
    @field_validator('table_name')
    @classmethod
    def validate_table_name(cls, v: str) -> str:
        if not v.replace('_', '').isalnum():
            error_msg = f"Nome tabella non valido: {v}. Deve contenere solo lettere, numeri e underscore"
            logger.error(error_msg)
            raise ValueError("Il nome della tabella può contenere solo lettere, numeri e underscore")
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "User",
                "table_name": "users",
                "fields": [
                    {
                        "field_name": "username",
                        "field_entity_id": 1,
                        "field_type": "string",
                        "required": True
                    },
                    {
                        "field_name": "email",
                        "field_entity_id": 1,
                        "field_type": "string",
                        "required": True
                    }
                ]
            }
        }

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    table_name: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated User",
                "table_name": "updated_users",
                "fields": [
                    {"name": "username", "type": "string", "required": True},
                    {"name": "email", "type": "string", "required": True}
                ]
            }
        }

class EntityFieldResponse(BaseModel):
    id: int
    field_name: str
    field_entity_id: int
    field_type: str
    required: bool
    default_value: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EntityResponse(BaseModel):
    id: int
    name: str
    table_name: str
    fields: List[EntityFieldResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Funzioni di accesso al database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_entity(db: Session, entity_id: int):
    return db.query(Entity).filter(Entity.id == entity_id).first()

def get_entity_by_name(db: Session, name: str):
    return db.query(Entity).filter(Entity.name == name).first()

def get_entities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Entity).offset(skip).limit(limit).all()

def create_entity(db: Session, entity: EntityCreate):
    try:
        # Create the main entity
        db_entity = Entity(
            name=entity.name,
            table_name=entity.table_name
        )
        db.add(db_entity)
        db.flush()  # Flush to get the entity ID
        
        # Create the entity fields
        for field in entity.fields:
            db_field = EntityField(
                entity_id=db_entity.id,
                field_entity_id=field.field_entity_id,
                field_name=field.field_name,
                field_type=field.field_type,
                required=field.required,
                default_value=field.default_value
            )
            db.add(db_field)
        
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Errore durante la creazione dell'entità: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante la creazione dell'entità: {str(e)}"
        )

def update_entity(db: Session, entity_id: int, entity_update: EntityUpdate):
    try:
        db_entity = get_entity(db, entity_id)
        if not db_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entità con ID {entity_id} non trovata"
            )
        
        # Update basic entity fields
        if entity_update.name is not None:
            db_entity.name = entity_update.name
        if entity_update.table_name is not None:
            db_entity.table_name = entity_update.table_name
        
        # Update fields if provided
        if entity_update.fields is not None:
            # Delete existing fields
            for field in db_entity.fields:
                db.delete(field)
            
            # Create new fields
            for field in entity_update.fields:
                db_field = EntityField(
                    entity_id=db_entity.id,
                    field_entity_id=field.field_entity_id,
                    field_name=field.field_name,
                    field_type=field.field_type,
                    required=field.required,
                    default_value=field.default_value
                )
                db.add(db_field)
        
        db.commit()
        db.refresh(db_entity)
        return db_entity
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Errore durante l'aggiornamento dell'entità: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento dell'entità: {str(e)}"
        )

def delete_entity(db: Session, entity_id: int):
    try:
        db_entity = get_entity(db, entity_id)
        if not db_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entità con ID {entity_id} non trovata"
            )
        
        # The cascade="all, delete-orphan" in the relationship will handle deleting the fields
        db.delete(db_entity)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Errore durante l'eliminazione dell'entità: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'eliminazione dell'entità: {str(e)}"
        )

class GenerationResult(BaseModel):
    """Modello per la risposta dell'endpoint di generazione."""
    success: bool
    message: str
    generated_tables: List[str] = []
    errors: List[Dict[str, str]] = []
    
    class Config:
        from_attributes = True

class DatabaseManager:
    """Classe per gestire le operazioni sul database dell'applicazione."""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def generate_tables(self, entities: List[Entity]) -> GenerationResult:
        result = GenerationResult(success=True, message="Generazione tabelle completata con successo")
        
        try:
            # Create a new metadata object for this generation
            metadata = MetaData()
            
            # First pass: Create all entity tables
            entity_tables = {}
            for entity in entities:
                try:
                    # Create columns for the entity
                    columns = [
                        Column('id', Integer, primary_key=True, index=True),
                        Column('created_at', DateTime, default=datetime.utcnow),
                        Column('updated_at', DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
                    ]
                    
                    # Add columns for each field
                    for field in entity.fields:
                        # Get the field type from the referenced entity
                        field_entity = next((e for e in entities if e.id == field.field_entity_id), None)
                        if not field_entity:
                            raise ValueError(f"Entity field {field.field_name} references non-existent entity {field.field_entity_id}")
                        
                        # Map the field type to SQLAlchemy type
                        column_type = self._get_column_type(field.field_type)
                        column = Column(
                            field.field_name,
                            column_type,
                            nullable=not field.required,
                            default=field.default_value if field.default_value else None
                        )
                        columns.append(column)
                    
                    # Create the table
                    table = Table(entity.table_name, metadata, *columns)
                    entity_tables[entity.id] = table
                    result.generated_tables.append(entity.table_name)
                    
                except Exception as e:
                    error_msg = f"Errore durante la generazione della tabella {entity.table_name}: {str(e)}"
                    logger.error(error_msg)
                    result.errors.append({"table": entity.table_name, "error": error_msg})
                    result.success = False
            
            # Second pass: Create foreign key relationships
            for entity in entities:
                try:
                    table = entity_tables[entity.id]
                    for field in entity.fields:
                        # If the field references another entity, create a foreign key
                        if field.field_entity_id != entity.id:  # Avoid self-referential foreign keys
                            referenced_table = entity_tables[field.field_entity_id]
                            foreign_key = ForeignKey(f"{referenced_table.name}.id")
                            column = Column(f"{field.field_name}_id", Integer, foreign_key)
                            table.append_column(column)
                    
                except Exception as e:
                    error_msg = f"Errore durante la creazione delle relazioni per {entity.table_name}: {str(e)}"
                    logger.error(error_msg)
                    result.errors.append({"table": entity.table_name, "error": error_msg})
                    result.success = False
            
            # Create all tables
            metadata.create_all(self.engine)
            
            if not result.success:
                result.message = "Generazione tabelle completata con errori"
            return result
            
        except Exception as e:
            error_msg = f"Errore generale durante la generazione delle tabelle: {str(e)}"
            logger.error(error_msg)
            result.success = False
            result.message = error_msg
            return result

    def _get_column_type(self, field_type: str):
        type_mapping = {
            "string": String,
            "integer": Integer,
            "float": Float,
            "boolean": Boolean,
            "date": DateTime,
            "datetime": DateTime,
            "json": JSON
        }
        return type_mapping.get(field_type.lower(), String)

# Creazione dell'app FastAPI
app = FastAPI(
    title="Entity Service",
    description="Servizio per la gestione di entità dinamiche",
    version="1.0.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints per le entità
@app.post("/generate", response_model=GenerationResult)
async def generate_database_tables(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Genera le tabelle nel database dell'applicazione basate sulle entità definite
    ed esegue le migrazioni necessarie.
    """
    try:
        # Recupera tutte le entità dal database
        entities = get_entities(db)
        if not entities:
            return GenerationResult(
                success=False,
                message="Nessuna entità trovata nel database"
            )
        
        # Crea un'istanza del gestore del database
        db_manager = DatabaseManager(settings.APP_DATABASE_URL)
        
        # Esegui la generazione delle tabelle
        result = db_manager.generate_tables(entities)
        
        # Esegui le migrazioni per il database dell'applicazione
        try:
            from alembic.config import Config
            from alembic import command
            
            # Configura Alembic
            alembic_cfg = Config("alembic.ini")
            
            # Esegui la migrazione per il database dell'applicazione
            command.upgrade(alembic_cfg, "head")
            
            # Aggiungi informazioni sulle migrazioni al risultato
            if result.message:
                result.message += "\nMigrazioni del database completate con successo."
            else:
                result.message = "Migrazioni del database completate con successo."
                
        except Exception as e:
            logger.error(f"Errore durante le migrazioni del database: {str(e)}")
            result.success = False
            if result.message:
                result.message += f"\nErrore durante le migrazioni: {str(e)}"
            else:
                result.message = f"Errore durante le migrazioni: {str(e)}"
        
        return result
        
    except Exception as e:
        logger.error(f"Errore durante la generazione del database: {str(e)}")
        return GenerationResult(
            success=False,
            message=f"Errore durante la generazione del database: {str(e)}"
        )

@app.post("/entities/", response_model=EntityResponse)
def create_entity_endpoint(entity: EntityCreate, db: Session = Depends(get_db)):
    try:
        logger.info("\n" + "="*50)
        logger.info("INIZIO CREAZIONE ENTITÀ - ENDPOINT")
        logger.info(f"Dati ricevuti: {entity}")
        logger.info(f"Tipo dati: {type(entity)}")
        
        # Verifica se esiste già un'entità con lo stesso nome
        db_entity = get_entity_by_name(db, name=entity.name)
        if db_entity:
            error_msg = f"Esiste già un'entità con il nome: {entity.name}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Log dettagliato dei campi
        if hasattr(entity, 'model_dump'):
            entity_dict = entity.model_dump()
            logger.info(f"Dati convertiti in dict: {entity_dict}")
            if 'fields' in entity_dict:
                logger.info(f"Numero campi: {len(entity_dict['fields'])}")
                for i, field in enumerate(entity_dict['fields']):
                    logger.info(f"Campo {i}: {field}")
        
        # Chiamata alla funzione di creazione
        logger.info("Chiamata a create_entity...")
        result = create_entity(db=db, entity=entity)
        
        logger.info("Entità creata con successo!")
        logger.info("="*50 + "\n")
        return result
    except HTTPException as he:
        # Rilancia direttamente le eccezioni HTTP
        logger.error(f"Errore HTTP durante la creazione: {str(he)}")
        raise
    except Exception as e:
        logger.error("ERRORE DURANTE LA CREAZIONE DELL'ENTITÀ - ENDPOINT", exc_info=True)
        logger.error(f"Tipo di eccezione: {type(e).__name__}")
        logger.error(f"Dettaglio errore: {str(e)}")
        if hasattr(entity, 'model_dump'):
            logger.error(f"Dati che hanno causato l'errore: {entity.model_dump()}")
        logger.info("="*50 + "\n")
        # Rilancia l'eccezione con un messaggio generico
        raise HTTPException(status_code=422, detail=str(e))
    return create_entity(db=db, entity=entity)

@app.get("/entities/", response_model=List[EntityResponse])
def read_entities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_entities(db, skip=skip, limit=limit)

@app.get("/entities/{entity_id}", response_model=EntityResponse)
def read_entity(entity_id: int, db: Session = Depends(get_db)):
    db_entity = get_entity(db, entity_id=entity_id)
    if db_entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return db_entity

@app.put("/entities/{entity_id}", response_model=EntityResponse)
def update_entity_endpoint(
    entity_id: int, entity_update: EntityUpdate, db: Session = Depends(get_db)
):
    try:
        logger.info(f"Aggiornamento entità ID: {entity_id}")
        logger.info(f"Dati ricevuti: {entity_update}")
        
        # Verifica che l'entità esista
        db_entity = get_entity(db, entity_id=entity_id)
        if db_entity is None:
            raise HTTPException(status_code=404, detail="Entità non trovata")
        
        # Prepara i dati per l'aggiornamento
        update_data = entity_update.dict(exclude_unset=True)
        
        # Se ci sono campi da aggiornare, converti il formato
        if 'fields' in update_data and update_data['fields'] is not None:
            fields_dict = {}
            for field in update_data['fields']:
                if isinstance(field, dict) and 'name' in field:
                    field_data = {
                        'type': field.get('type', 'string'),
                        'required': field.get('required', False)
                    }
                    if 'default' in field:
                        field_data['default'] = field['default']
                    fields_dict[field['name']] = field_data
            update_data['fields'] = fields_dict
        
        logger.info(f"Dati elaborati per l'aggiornamento: {update_data}")
        
        # Aggiorna l'entità
        for field, value in update_data.items():
            setattr(db_entity, field, value)
        
        db.commit()
        db.refresh(db_entity)
        
        logger.info(f"Entità aggiornata con successo: {db_entity}")
        return db_entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento dell'entità: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore durante l'aggiornamento dell'entità: {str(e)}"
        )

@app.delete("/entities/{entity_id}")

# Endpoint di benvenuto
@app.get("/")
async def root():
    return {
        "message": "Entity Service",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Avvio del server
if __name__ == "__main__":
    uvicorn.run(
        "entities:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
        log_level="debug" if settings.ENVIRONMENT == "development" else "info"
    )
