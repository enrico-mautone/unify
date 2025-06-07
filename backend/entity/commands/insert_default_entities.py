from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Entity as EntityModel

def insert_default_entities():
    """
    Inserisce le entità di sistema predefinite (Users e Pages) con i relativi campi
    se non esistono già nel database.
    """
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if Users entity exists
        users_entity = db.query(EntityModel).filter_by(name="Users").first()
        if not users_entity:
            print("Creating Users entity...")
            users_entity = EntityModel(
                name="Users",
                description="System entity for managing users",
                table_name="users",
                is_field=False,
                is_page=False,
                parent_id=None
            )
            db.add(users_entity)
            db.flush()
            
            # Create email field
            email_field = EntityModel(
                name="email",
                description="User's email address",
                table_name=None,  # Non serve per i campi
                is_field=True,
                is_page=False,
                parent_id=users_entity.id,
                field_type="string",
                required=True,
                default_value=None,
                unique=True
            )
            db.add(email_field)
            
            # Create password field
            password_field = EntityModel(
                name="password",
                description="User's hashed password",
                table_name=None,  # Non serve per i campi
                is_field=True,
                is_page=False,
                parent_id=users_entity.id,
                field_type="password",
                required=True,
                default_value=None,
                unique=False
            )
            db.add(password_field)
            
            # Esegui il commit per salvare le modifiche
            db.commit()
            print("Users entity and fields created and committed to database")
        
        # Check if Pages entity exists
        pages_entity = db.query(EntityModel).filter_by(name="Pages").first()
        if not pages_entity:
            print("Creating Pages entity...")
            pages_entity = EntityModel(
                name="Pages",
                description="System entity for managing pages",
                table_name="pages",
                is_field=False,
                is_page=False,
                parent_id=None
            )
            db.add(pages_entity)
            db.flush()
            
            # Define page fields
            page_fields = [
                {
                    "name": "title",
                    "description": "Page title",
                    "field_type": "string",
                    "required": True,
                    "default_value": None,
                    "unique": False
                },
                {
                    "name": "slug",
                    "description": "URL-friendly page identifier",
                    "field_type": "string",
                    "required": True,
                    "default_value": None,
                    "unique": True
                },
                {
                    "name": "entity_type",
                    "description": "Entity type to display",
                    "field_type": "string",
                    "required": True,
                    "default_value": None,
                    "unique": False
                },
                {
                    "name": "layout",
                    "description": "Page layout configuration",
                    "field_type": "json",
                    "required": True,
                    "default_value": None,  # Non usare un valore predefinito per JSON in SQLite
                    "unique": False
                },
                {
                    "name": "items_per_page",
                    "description": "Number of items per page",
                    "field_type": "integer",
                    "required": False,
                    "default_value": "10",
                    "unique": False
                }
            ]
            
            # Create page fields
            for field_data in page_fields:
                field = EntityModel(
                    name=field_data["name"],
                    description=field_data["description"],
                    table_name=None,  # Non serve per i campi
                    is_field=True,
                    is_page=False,
                    parent_id=pages_entity.id,
                    field_type=field_data["field_type"],
                    required=field_data.get("required", False),
                    default_value=str(field_data.get("default_value", "")) if field_data.get("default_value") is not None else None,
                    unique=field_data.get("unique", False)
                )
                db.add(field)
            
            # Esegui il commit per salvare le modifiche
            db.commit()
            print("Pages entity and fields created and committed to database")
        
        db.commit()
        print("System entities verified")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error verifying system entities: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    insert_default_entities()
