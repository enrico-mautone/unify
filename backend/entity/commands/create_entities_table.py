from sqlalchemy import inspect as sql_inspect, text
from database import engine, Base, SessionLocal
from models import Entity  # Import esplicito del modello Entity

def create_entities_table():
    """
    Crea o aggiorna la tabella delle entità basata sul modello SQLAlchemy
    """
    inspector = sql_inspect(engine)
    table_name = Entity.__tablename__
    
    with engine.connect() as conn:
        # Disabilita i vincoli di chiave esterna per SQLite
        conn.execute(text('PRAGMA foreign_keys=OFF'))
        
        # Se la tabella esiste, la elimina
        if inspector.has_table(table_name):
            print(f"Dropping existing '{table_name}' table...")
            Entity.__table__.drop(engine)
        
        # Crea la tabella con lo schema corretto
        print(f"Creating '{table_name}' table from model...")
        Entity.metadata.create_all(bind=engine, tables=[Entity.__table__])
        print(f"'{table_name}' table created successfully")
        
        # Riabilita i vincoli di chiave esterna
        conn.execute(text('PRAGMA foreign_keys=ON'))
    
    return True

if __name__ == "__main__":
    create_entities_table()
