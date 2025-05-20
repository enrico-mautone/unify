import sys
from pathlib import Path

# Aggiungi la cartella backend al path di Python
sys.path.append(str(Path(__file__).parent))

from auth.database import SessionLocal
from auth.models import User
from auth.auth import get_password_hash

def create_user():
    db = SessionLocal()
    try:
        # Verifica se l'utente esiste già
        existing_user = db.query(User).filter(User.email == "super.unify@purpleswan.com").first()
        if existing_user:
            print("L'utente esiste già nel database.")
            return

        # Crea il nuovo utente
        hashed_password = get_password_hash("password01!")
        new_user = User(
            email="super.unify@purpleswan.com",
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        print("Utente creato con successo!")
        print(f"Email: super.unify@purpleswan.com")
        
    except Exception as e:
        db.rollback()
        print(f"Errore durante la creazione dell'utente: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creazione dell'utente in corso...")
    create_user()
