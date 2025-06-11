"""
Comando per configurare le pagine predefinite del sistema.
"""
import json
import os
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

# Aggiungi la directory radice del progetto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from entity.database import SessionLocal, engine

def load_json_layout(file_path):
    """Carica un layout da un file JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Errore: File non trovato: {file_path}")
        raise
    except json.JSONDecodeError:
        print(f"Errore: Il file {file_path} non è un JSON valido")
        raise
    except Exception as e:
        print(f"Errore durante il caricamento del file {file_path}: {str(e)}")
        raise

def setup_default_pages():
    """
    Crea e configura le pagine predefinite del sistema.
    """
    db = None
    try:
        print("Setting up default pages...")
        
        # Percorso del file di layout della pagina di login
        login_layout_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'login_layout.json'
        )
        
        # Carica il layout della pagina di login dal file JSON
        login_page_layout = load_json_layout(login_layout_path)
        print(f"Layout della pagina di login caricato da: {login_layout_path}")
        
        # Salva il layout nel database
        db = SessionLocal()
        db.execute(text("""
            INSERT INTO pages (title, slug, layout, created_at, updated_at, entity_type)
            VALUES (:title, :slug, :layout, :now, :now, NULL)
            ON CONFLICT (slug) DO UPDATE 
            SET layout = :layout, updated_at = :now
        """), {
            'title': 'Login',
            'slug': 'login',
            'layout': json.dumps(login_page_layout),
            'now': datetime.utcnow()
        })
        db.commit()
        
        print("Default pages setup completed successfully!")
        return login_page_layout
        
    except Exception as e:
        print(f"Errore durante la configurazione delle pagine predefinite: {str(e)}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    setup_default_pages()
