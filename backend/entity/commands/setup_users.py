from sqlalchemy.orm import Session
from sqlalchemy import text, Table, Column, Integer, String, MetaData, create_engine
from database import SessionLocal, engine
from passlib.context import CryptContext

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def setup_users():
    db = SessionLocal()
    try:
        # Ensure users table exists
        metadata = MetaData()
        users_table = Table('users', metadata,
            Column('id', Integer, primary_key=True),
            Column('email', String, unique=True, nullable=False),
            Column('password', String, nullable=False)
        )
        users_table.create(bind=engine, checkfirst=True)
        
        # Insert default user
        super_user_email = "super.unify@purpleswan.com"
        super_user_password = get_password_hash("password01!")
        
        # First check if user already exists
        result = db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": super_user_email}
        ).fetchone()
        
        if not result:
            insert_super_user_sql = """
            INSERT INTO users (email, password)
            VALUES (:email, :password)
            """
            db.execute(
                text(insert_super_user_sql),
                {"email": super_user_email, "password": super_user_password}
            )
            db.commit()
            print(f"Default user created with email: {super_user_email}")
        else:
            print(f"User with email {super_user_email} already exists")
    except Exception as e:
        db.rollback()
        print(f"Error creating default user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_users() 