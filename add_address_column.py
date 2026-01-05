from sqlalchemy import text, inspect
from app.database import engine

def add_address_column():
    inspector = inspect(engine)
    
    with engine.begin() as connection:
        # Check bookings table
        columns = [c['name'] for c in inspector.get_columns('bookings')]
        if 'address' not in columns:
            try:
                connection.execute(text("ALTER TABLE bookings ADD COLUMN address TEXT"))
                print("Successfully added 'address' column to 'bookings' table.")
            except Exception as e:
                print(f"Error adding 'address' to 'bookings': {e}")
        else:
            print("'address' column already exists in 'bookings'.")

        # Check providers table
        columns = [c['name'] for c in inspector.get_columns('providers')]
        if 'address' not in columns:
            try:
                connection.execute(text("ALTER TABLE providers ADD COLUMN address TEXT"))
                print("Successfully added 'address' column to 'providers' table.")
            except Exception as e:
                print(f"Error adding 'address' to 'providers': {e}")
        else:
            print("'address' column already exists in 'providers'.")

if __name__ == "__main__":
    add_address_column()
