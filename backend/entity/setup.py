import os
from pathlib import Path

def setup():
    try:
        # Assicurati che la directory di lavoro sia corretta
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Step 1: Reset database
        print("Step 1: Resetting database...")
        try:
            from commands.reset_db import reset_db
            reset_db()
            print("Database reset completed")
        except Exception as e:
            print(f"Error resetting database: {str(e)}")
            import traceback
            traceback.print_exc()
            return
            
        # Step 2: Create entities table
        print("\nStep 2: Creating entities table...")
        try:
            from commands.create_entities_table import create_entities_table
            create_entities_table()
            print("Entities table created successfully")
        except Exception as e:
            print(f"Error creating entities table: {str(e)}")
            import traceback
            traceback.print_exc()
            return
            
        # Step 3: Insert default entities
        print("\nStep 3: Inserting default entities...")
        try:
            from commands.insert_default_entities import insert_default_entities
            insert_default_entities()
            print("Default entities inserted successfully")
        except Exception as e:
            print(f"Error inserting default entities: {str(e)}")
            import traceback
            traceback.print_exc()
            return
            
        # Step 4: Generate entity migrations
        print("\nStep 4: Generating entity migrations...")
        try:
            from commands.generate_entity_migrations import generate_entity_migrations
            generate_entity_migrations()
            print("Entity migrations generated successfully")
        except Exception as e:
            print(f"Error generating entity migrations: {str(e)}")
            import traceback
            traceback.print_exc()
            return
            
        # Step 5: Run migrations to create entity tables
        print("\nStep 5: Running migrations to create entity tables...")
        try:
            from commands.run_migrations import run_migrations
            run_migrations()
            print("Entity tables created successfully")
        except Exception as e:
            print(f"Error creating entity tables: {str(e)}")
            import traceback
            traceback.print_exc()
            return

    except Exception as e:
        print(f"Error during setup: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    setup()