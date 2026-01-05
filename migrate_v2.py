from sqlalchemy import text, inspect
from app.database import engine

def migrate_v2():
    inspector = inspect(engine)
    
    with engine.begin() as connection:
        # Update providers table
        columns = [c['name'] for c in inspector.get_columns('providers')]
        if 'earnings' not in columns:
            connection.execute(text("ALTER TABLE providers ADD COLUMN earnings FLOAT DEFAULT 0.0"))
            print("Added 'earnings' to providers.")

        # Update bookings table
        columns = [c['name'] for c in inspector.get_columns('bookings')]
        if 'commission_amount' not in columns:
            connection.execute(text("ALTER TABLE bookings ADD COLUMN commission_amount FLOAT DEFAULT 0.0"))
            print("Added 'commission_amount' to bookings.")
        if 'provider_amount' not in columns:
            connection.execute(text("ALTER TABLE bookings ADD COLUMN provider_amount FLOAT DEFAULT 0.0"))
            print("Added 'provider_amount' to bookings.")

if __name__ == "__main__":
    migrate_v2()
