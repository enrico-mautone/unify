from typing import Optional
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base, backref

Base = declarative_base()

class Entity(Base):
    """
    Modello base per tutte le entità del sistema.
    Può rappresentare un'entità, un campo o una pagina a seconda dei flag.
    """
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(String(500), nullable=True)
    table_name = Column(String(50), unique=True, nullable=True)  # Nullable per i campi
    
    # Flags per il tipo di entità
    is_field = Column(Boolean, default=False, nullable=False)
    is_page = Column(Boolean, default=False, nullable=False)
    
    # Relazioni
    parent_id = Column(Integer, ForeignKey('entities.id'), nullable=True)
    parent = relationship(
        "Entity", 
        remote_side=[id],
        foreign_keys=[parent_id],
        backref=backref("children", lazy='dynamic')
    )
    
    # Campi per i campi (se is_field=True)
    field_type = Column(String(50), nullable=True)  # string, integer, boolean, ecc.
    required = Column(Boolean, default=False)
    default_value = Column(String(500), nullable=True)
    unique = Column(Boolean, default=False)
    
    # Relazione con i campi (se è un'entità)
    fields = relationship(
        "Entity",
        # Campo è un'entità che ha questa entità come genitore ed è contrassegnato come campo
        primaryjoin="and_(Entity.parent_id==Entity.id, Entity.is_field==True)",
        foreign_keys="[Entity.parent_id]",
        viewonly=True,
        lazy='dynamic'
    )
    
    def __repr__(self):
        entity_type = "page" if self.is_page else "field" if self.is_field else "entity"
        return f"<Entity {self.name} (type: {entity_type}, table: {self.table_name})>"
