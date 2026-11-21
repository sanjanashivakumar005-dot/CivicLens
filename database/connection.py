
from database.connection import engine, Base

# Import all models so SQLAlchemy registers the tables
from database.models import User, Issue, Media, StatusLog, Vote

def initialize_database():
    print("Initializing CivicLens database...")

    try:
        Base.metadata.create_all(bind=engine)

        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print("\nDatabase initialization completed!")
        print("Tables created/found:")

        for table in tables:
            print(f"  [OK] {table}")

        if tables:
            print("\nCivicLens database is ready!")
        else:
            print("\nWARNING: No tables were created.")

    except Exception as e:
        import traceback
        print("\nDatabase initialization failed!")
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    initialize_database()
