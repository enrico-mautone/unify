import os
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, JSON, 
    ForeignKey, inspect, DateTime, Float, Text, Date, 
    Time, LargeBinary, Numeric, BigInteger, SmallInteger
)
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Dict, Any, Optional, Type

def get_sqlalchemy_type(field_type: str):
    """
    Convert a field type string to the corresponding SQLAlchemy type.
    
    Args:
        field_type: String representing the field type
        
    Returns:
        SQLAlchemy column type
    """
    type_mapping = {
        'string': String(255),
        'text': Text(),
        'integer': Integer(),
        'bigint': BigInteger(),
        'smallint': SmallInteger(),
        'float': Float(),
        'numeric': Numeric(),
        'boolean': Boolean(),
        'date': Date(),
        'datetime': DateTime(),
        'time': Time(),
        'json': JSON(),
        'binary': LargeBinary(),
        'password': String(255),  # Store hashed passwords as strings
        'email': String(255),     # Email is just a specialized string
        'slug': String(255),      # Slug is a URL-friendly string
    }
    
    # Default to Text if type is not recognized
    return type_mapping.get(field_type.lower(), Text())

# Import database components
from database import engine, Base
from models import Entity

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def prepare_migrations_directory():
    """
    Prepare the migrations directory by removing existing migrations and creating
    the necessary directory structure.
    
    Returns:
        str: Path to the migrations versions directory
    """
    # Get the project root directory (one level up from commands)
    project_root = Path(__file__).parent.parent
    migrations_dir = project_root / 'migrations'
    versions_dir = migrations_dir / 'versions'
    
    # Remove existing migrations if they exist
    if migrations_dir.exists():
        print("Removing existing migrations...")
        shutil.rmtree(migrations_dir)
        print("Existing migrations removed")
    
    # Create migrations/versions directory structure
    versions_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created migrations directory at: {migrations_dir}")
    
    # Create empty __init__.py files to make it a Python package
    (migrations_dir / '__init__.py').touch()
    (versions_dir / '__init__.py').touch()
    
    return str(versions_dir)


def ensure_alembic_version():
    """Ensure the alembic_version table exists in the database."""
    inspector = inspect(engine)
    if not inspector.has_table('alembic_version'):
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) NOT NULL,
                    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
                )
            
"""))
            conn.commit()

def get_last_migration() -> Optional[str]:
    """Get the last migration revision from the database."""
    inspector = inspect(engine)
    if not inspector.has_table('alembic_version'):
        return None
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1"))
        row = result.fetchone()
        return row[0] if row else None

def generate_entity_migrations():
    """
    Generate migrations for root entities and their fields.
    This will first clean up any existing migrations and then generate new ones.
    """
    # Prepare migrations directory
    versions_dir = prepare_migrations_directory()
    
    # Ensure alembic_version table exists
    ensure_alembic_version()
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Get last revision from database
        last_revision = get_last_migration()
        print(f"Last migration in database: {last_revision or 'None'}")
        
        # Get all root entities (those with no parent) ordered by ID
        root_entities = db.query(Entity).filter(Entity.parent_id == None).order_by(Entity.id).all()
        
        if not root_entities:
            print("\nNo root entities found to generate migrations for")
            return
            
        print(f"\nFound {len(root_entities)} root entities to process:")
        for e in root_entities:
            print(f"- {e.name} (ID: {e.id}, is_page: {e.is_page})")
        
        # Create migrations directory if it doesn't exist
        os.makedirs(versions_dir, exist_ok=True)
            
        # Process each root entity
        for entity in root_entities:
            print(f"\nProcessing entity: {entity.name} (ID: {entity.id})")
            
            # Get all fields for this entity (direct children with is_field=True)
            fields = db.query(Entity).filter(
                Entity.parent_id == entity.id,
                Entity.is_field == True
            ).all()
            
            print(f"Found {len(fields)} fields for {entity.name}")
            
            # Generate migration for this entity
            try:
                migration_file = generate_entity_migration(entity, fields, last_revision, versions_dir)
                if migration_file:
                    # Update last_revision to point to the newly created migration
                    last_revision = os.path.basename(migration_file).split('.')[0]
                    print(f"Generated migration: {migration_file}")
                    print(f"Updated last_revision to: {last_revision}")
                else:
                    print(f"Skipping migration for {entity.name} - migration already exists")
                    
            except Exception as e:
                print(f"Error generating migration for {entity.name}: {str(e)}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Error generating migrations: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()
    
    print("\nMigration generation complete.")
    if last_revision:
        print(f"Last migration revision: {last_revision}")
    else:
        print("No migrations were generated.")

def generate_entity_migration(entity, fields, last_revision, migrations_dir):
    """
    Generate a migration file for a single entity with its fields.
    
    Args:
        entity: The root entity to generate migration for
        fields: List of field entities that belong to this entity
        last_revision: Last migration revision to chain from
        migrations_dir: Directory to save migration files
    
    Returns:
        str: Path to the generated migration file
    """
    # Generate migration content
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_name = f"create_{entity.table_name}_table"
    revision_id = f"{timestamp}_{hash(entity.name) % 10000:04d}_{migration_name}"
    filename = f"{revision_id}.py"
    filepath = os.path.join(migrations_dir, filename)
    
    if os.path.exists(filepath):
        print(f"Migration already exists: {filepath}")
        return filepath
        
    # Generate columns for the table
    columns = [
        ("id", Integer(), {"primary_key": True, "nullable": False}),
        ("created_at", DateTime(), {"server_default": "sa.text('(CURRENT_TIMESTAMP)')", "nullable": False}),
        ("updated_at", DateTime(), {"server_default": "sa.text('(CURRENT_TIMESTAMP)')", "nullable": False})
    ]
    
    # Add entity fields as columns
    for field in fields:
        # Get field properties directly from the field entity
        field_type = field.field_type or 'string'
        required = field.required if field.required is not None else False
        default_value = field.default_value
        unique = field.unique if field.unique is not None else False
        
        # Get SQLAlchemy type for the field
        col_type = get_sqlalchemy_type(field_type)
        col_args = {"nullable": not required}
        
        if unique:
            col_args["unique"] = True
            
        # Special handling for JSON fields - don't set default value in the schema
        if field_type.lower() != 'json' and default_value is not None:
            try:
                # Try to evaluate as Python literal (numbers, booleans, etc.)
                import ast
                default_val = ast.literal_eval(str(default_value))
                if isinstance(default_val, (int, float, bool)):
                    col_args["server_default"] = f"'{default_val}'"
                else:
                    escaped_val = str(default_val).replace("'", "''")
                    col_args["server_default"] = f"'{escaped_val}'"
            except (ValueError, SyntaxError):
                # If parsing fails, treat as simple string
                escaped_val = str(default_value).replace("'", "''")
                col_args["server_default"] = f"'{escaped_val}'"
                    
        # Use the field name as column name
        column_name = field.name.lower().replace(' ', '_')
        columns.append((column_name, col_type, col_args))
    
    # Generate migration file content
    columns_str = []
    json_defaults = []  # To store JSON defaults that need special handling
    
    for name, sa_type, args in columns:
        # For String types, use sa.String() with length if specified
        if hasattr(sa_type, '__visit_name__'):
            type_name = sa_type.__class__.__name__
            if type_name == 'String':
                length = sa_type.length if hasattr(sa_type, 'length') else 255
                type_str = f"sa.String({length})"
            else:
                type_str = f"sa.{type_name}()"
        else:
            type_name = sa_type.__class__.__name__
            type_str = f"sa.{type_name}()"
        
        # Check if this column has a JSON default that needs special handling
        json_default = args.pop('json_default', None)
        if json_default is not None:
            # Store the JSON default for later use in the migration
            json_defaults.append((name, json_default))
        
        # Format column definition
        col_args = []
        for k, v in args.items():
            # Convert Python booleans to proper Python syntax
            if v is True:
                col_args.append(f"{k}=True")
            elif v is False:
                col_args.append(f"{k}=False")
            elif k == 'server_default' and v is not None:
                if isinstance(v, str):
                    if v.startswith("sa.text('"):
                        col_args.append(f"{k}={v}")
                    else:
                        # For numeric values, don't add quotes, but always as string for server_default
                        if v.isdigit() or (v.startswith("'") and v.endswith("'") and v[1:-1].isdigit()):
                            clean_v = v[1:-1] if v.startswith("'") and v.endswith("'") else v
                            col_args.append(f'{k}="{clean_v}"')
                        else:
                            col_args.append(f"{k}='{v}'")
                else:
                    # For int/float/bool: always use string for server_default
                    col_args.append(f'{k}="{v}"')
            elif isinstance(v, bool):
                col_args.append(f"{k}={str(v).lower()}")
            elif v is None:
                col_args.append(f"{k}=None")
            elif isinstance(v, str):
                col_args.append(f"{k}='{v}'")
            else:
                col_args.append(f"{k}={v}")
        
        columns_str.append(f"sa.Column('{name}', {type_str}, {', '.join(col_args)})")
    
    columns_str = ',\n        '.join(columns_str)
    
    # Prepare JSON default updates if any
    json_updates = ''
    if json_defaults:
        json_updates = '\n    # Set JSON default values\n'
        for col_name, default_value in json_defaults:
            import json
            json_str = json.dumps(default_value, ensure_ascii=False)
            json_str = json_str.replace("'", "\\'")
            json_updates += f'    op.execute(\'\'\'UPDATE {entity.table_name} SET {col_name} = \'{json_str}\' WHERE {col_name} IS NULL\'\'\')\n'

    migration_content = f'''"""{migration_name}

Revision ID: {revision_id}
Revises: {last_revision or 'None'}
Create Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = {repr(last_revision) if last_revision else 'None'}
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        '{entity.table_name}',
        {columns_str}
    )
    
    {json_updates}
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('{entity.table_name}')
    # ### end Alembic commands ###

'''
    # Write migration file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    return filepath
