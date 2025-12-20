from sqlalchemy import text
from app.database import engine

def add_complaints_table():
    with engine.begin() as connection:
        try:
            # Create complaints table
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS complaints (
                    id SERIAL PRIMARY KEY,
                    booking_id INTEGER REFERENCES bookings(id),
                    customer_id INTEGER REFERENCES users(id),
                    subject VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    resolution TEXT,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Successfully created complaints table.")
        except Exception as e:
            print(f"Error creating complaints table: {e}")

if __name__ == "__main__":
    add_complaints_table()
