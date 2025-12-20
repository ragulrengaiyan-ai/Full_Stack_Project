from sqlalchemy import text
from app.database import engine

def add_address_column():
    with engine.begin() as connection:
        try:
            connection.execute(text("ALTER TABLE bookings ADD COLUMN address TEXT"))
            print("Successfully added address column to bookings table.")
        except Exception as e:
            if "already exists" in str(e):
                print("Address column already exists.")
            else:
                print(f"Error adding address column: {e}")

if __name__ == "__main__":
    add_address_column()
