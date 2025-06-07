from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
import subprocess
import os

def reset_db():
    db = SessionLocal()
    try:
        # Step 0: Drop alembic_version table if it exists
        db.execute(text("DROP TABLE IF EXISTS alembic_version;"))
        
        # Step 1: Drop all tables except entities and alembic_version
        # For SQLite, we need to get the list of tables differently
        db.execute(text("PRAGMA foreign_keys = OFF"))  # Disable foreign key checks
        
        # Get list of all tables using SQLite's sqlite_master table
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT IN ('entities', 'alembic_version', 'sqlite_sequence')
        """))
        tables = [row[0] for row in result]

        # Drop each table
        for table in tables:
            try:
                db.execute(text(f'DROP TABLE IF EXISTS "{table}"'))
            except Exception as e:
                print(f"Warning: Could not drop table {table}: {e}")
        
        # Step 2: Delete all entities except Entity itself
        # First check if entities table exists
        result = db.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='entities'
        """)).fetchone()
        
        if result:  # Only try to delete if entities table exists
            db.execute(text("""
                DELETE FROM entities 
                WHERE name != 'Entity';
            """))
        
        db.execute(text("PRAGMA foreign_keys = ON"))  # Re-enable foreign key checks
        
        # Step 3: Reset alembic version to base
        migrations_dir = os.path.join(os.path.dirname(__file__), "..", "migrations")
        try:
            # Try to get the first revision
            result = subprocess.run(
                ["alembic", "history", "-i"],
                cwd=migrations_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # If we have migrations, get the first revision
                first_rev = result.stdout.strip().split('\n')[0].split('->')[0].strip()
                subprocess.run(
                    ["alembic", "downgrade", first_rev],
                    cwd=migrations_dir,
                    check=True
                )
                print(f"- Database version reset to '{first_rev}'")
            else:
                # If no migrations found, just stamp the base
                subprocess.run(
                    ["alembic", "stamp", "base"],
                    cwd=migrations_dir,
                    check=True
                )
                print("- Database stamped as base (no migrations found)")
                
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not reset migrations: {e}")
        
        db.commit()
        print("Database reset successfully to initial state")
        print("- All tables except 'entities' have been dropped")
        print("- All entities except 'Entity' have been removed")
        
    except Exception as e:
        db.rollback()
        print(f"Error resetting database: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_db() 