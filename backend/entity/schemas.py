from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ENTITY = "entity"  # New type for entity references

class FieldDefinition(BaseModel):
    name: str
    type: FieldType
    required: bool = True
    default: Optional[str] = None
    entity_id: Optional[int] = None  # Reference to another entity if type is ENTITY

class EntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    table_name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-z][a-z0-9_]*$')
    is_field: bool = False

class EntityCreate(EntityBase):
    parent_id: Optional[int] = None
    fields: Optional[Dict[str, FieldDefinition]] = None

class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    fields: Optional[Dict[str, FieldDefinition]] = None
    parent_id: Optional[int] = None

class EntityResponse(EntityBase):
    id: int
    parent_id: Optional[int]
    fields: Optional[Dict[str, FieldDefinition]]

    class Config:
        from_attributes = True

class EntityInstanceCreate(BaseModel):
    entity_id: int
    data: Dict[str, str]

class EntityInstanceUpdate(BaseModel):
    data: Dict[str, str]

class EntityInstanceResponse(BaseModel):
    id: int
    entity_id: int
    data: Dict[str, str]
