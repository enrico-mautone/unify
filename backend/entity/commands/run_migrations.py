import subprocess
import os
import shutil
from pathlib import Path

def ensure_migrations_setup():
    """Assicura che la struttura delle migrazioni sia configurata correttamente."""
    root_dir = Path(__file__).parent.parent
    migrations_dir = root_dir / "migrations"
    env_py = migrations_dir / "env.py"
    
    # Se la cartella migrations non esiste, la creiamo
    if not migrations_dir.exists():
        print("Creating migrations directory...")
        migrations_dir.mkdir()
    
    # Crea la directory versions se non esiste
    versions_dir = migrations_dir / "versions"
    if not versions_dir.exists():
        versions_dir.mkdir()
        
    # Crea un file __init__.py in versions se non esiste
    init_py = versions_dir / "__init__.py"
    if not init_py.exists():
        init_py.touch()
        
    # Crea il file script.py.mako se non esiste
    script_template = migrations_dir / "script.py.mako"
    if not script_template.exists():
        # Creiamo il contenuto del template come lista di righe per evitare problemi di escape
        template_lines = [
            '"""${message}',
            '',
            'Revision ID: ${up_revision}',
            'Revises: ${down_revision | comma,n}',
            'Create Date: ${create_date}',
            '',
            '"""',
            'from alembic import op',
            'import sqlalchemy as sa',
            '${imports if imports else ""}',
            '',
            '# revision identifiers, used by Alembic.',
            'revision = ${repr(up_revision)}',
            'down_revision = ${repr(down_revision)}',
            'branch_labels = ${repr(branch_labels)}',
            'depends_on = ${repr(depends_on)}',
            '',
            '',
            'def upgrade() -> None:',
            '    ${upgrades if upgrades else "pass"}',
            '',
            '',
            'def downgrade() -> None:',
            '    ${downgrades if downgrades else "pass"}' 
        ]
        
        # Scriviamo il file riga per riga
        with open(script_template, 'w', encoding='utf-8') as f:
            f.write('\n'.join(template_lines))
    
    # Crea o aggiorna env.py per escludere le tabelle non desiderate
    env_lines = [
        'from logging.config import fileConfig',
        'from sqlalchemy import engine_from_config',
        'from sqlalchemy import pool',
        'from alembic import context',
        'import os',
        'import sys',
        '',
        "# Aggiungi la directory principale al path Python",
        "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))",
        '',
        "# Importa i modelli SQLAlchemy",
        'from models import Base',
        '',
        "# this is the Alembic Config object, which provides",
        "# access to the values within the .ini file in use.",
        'config = context.config',
        '',
        "# Interpret the config file for Python logging.",
        "# This line sets up loggers basically.",
        'if config.config_file_name is not None:',
        '    fileConfig(config.config_file_name)',
        '',
        "# add your model's MetaData object here",
        "# for 'autogenerate' support",
        'target_metadata = Base.metadata',
        '',
        'def include_object(object, name, type_, reflected, compare_to):',
        "    # Escludi le tabelle che iniziano con 'entity_'",
        "    if type_ == 'table' and name and name.startswith('entity_'):",
        '        return False',
        '    return True',
        '',
        'def run_migrations_offline() -> None:',
        '    """Run migrations in \'offline\' mode."""',
        '    from database import SQLALCHEMY_DATABASE_URL',
        '    url = SQLALCHEMY_DATABASE_URL',
        '    context.configure(',
        '        url=url,',
        '        target_metadata=target_metadata,',
        '        literal_binds=True,',
        '        dialect_opts={"paramstyle": "named"},',
        '        include_object=include_object',
        '    )',
        '',
        '    with context.begin_transaction():',
        '        context.run_migrations()',
        '',
        'def run_migrations_online() -> None:',
        '    """Run migrations in \'online\' mode."""',
        '    from database import engine',
        '',
        '    with engine.connect() as connection:',
        '        context.configure(',
        '            connection=connection,',
        '            target_metadata=target_metadata,',
        '            include_object=include_object',
        '        )',
        '',
        '        with context.begin_transaction():',
        '            context.run_migrations()',
        '',
        'if context.is_offline_mode():',
        '    run_migrations_offline()',
        'else:',
        '    run_migrations_online()',
    ]
    
    with open(env_py, 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_lines))
    
    # Se esiste già env.py, verifichiamo che sia valido
    if env_py.exists():
        print("Alembic already initialized, checking configuration...")
        try:
            # Verifica che il file env.py contenga il contenuto minimo richiesto
            with open(env_py, 'r') as f:
                content = f.read()
                if 'target_metadata' in content and 'run_migrations_online' in content:
                    print("Alembic configuration looks good")
                    return True
                else:
                    print("Warning: env.py exists but seems incomplete")
        except Exception as e:
            print(f"Error checking env.py: {str(e)}")
    
    # Se siamo qui, dobbiamo creare o ricreare env.py
    print("Creating/updating env.py...")
    
    # Crea un env.py personalizzato
    env_content = '''
from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Aggiungi la directory principale al path Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa i modelli SQLAlchemy
from models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model\'s MetaData object here
# for \'autogenerate\' support
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in \'offline\' mode."""
    from database import SQLALCHEMY_DATABASE_URL
    url = SQLALCHEMY_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in \'online\' mode."""
    from database import engine

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    
    try:
        with open(env_py, 'w') as f:
            f.write(env_content.strip())
        print("env.py created/updated successfully")
        return True
    except Exception as e:
        print(f"Error creating env.py: {str(e)}")
        return False

def cleanup_old_migrations():
    """Pulisce le vecchie migrazioni per iniziare da zero."""
    root_dir = Path(__file__).parent.parent
    versions_dir = root_dir / "migrations" / "versions"
    
    # Elimina tutte le migrazioni tranne __init__.py
    if versions_dir.exists():
        print("Cleaning up old migrations...")
        for f in versions_dir.glob("*.py"):
            if f.name != "__init__.py":
                f.unlink()

def run_migrations():
    """Esegue le migrazioni esistenti per creare le tabelle delle entità."""
    try:
        root_dir = Path(__file__).parent.parent
        
        print("Setting up migrations structure...")
        if not ensure_migrations_setup():
            print("Failed to set up migrations structure")
            return False
        
        print("Checking for pending migrations...")
        
        # Verifica se ci sono migrazioni in sospeso
        result = subprocess.run(
            ["alembic", "current"],
            cwd=str(root_dir),
            capture_output=True,
            text=True
        )
        
        print(f"Current migration status: {result.stdout.strip()}")
        
        # Applica tutte le migrazioni in sospeso
        print("\n=== Applying pending migrations ===")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(root_dir),
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error applying migrations: {result.stderr}")
            return False
            
        print("Migrations applied successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {str(e)}")
        print(f"Output: {e.output}")
        print(f"Stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_migrations() 