import os
import re
from sqlalchemy import create_engine, text

def get_url():
    # Manually parse .env to be 100% sure we get it
    try:
        with open(".env", "r") as f:
            content = f.read()
            match = re.search(r"DATABASE_URL=['\"]?(.*?)['\"]?(\s|$)", content)
            if match:
                url = match.group(1).split('#')[0].strip() # Remove comments
                if url.startswith("postgres://"):
                    url = url.replace("postgres://", "postgresql://", 1)
                return url
    except Exception as e:
        print(f"Error reading .env: {e}")
    return os.environ.get("DATABASE_URL")

def migrate():
    url = get_url()
    if not url:
        print("FATAL: DATABASE_URL not found in .env or environment.")
        return

    print(f"Connecting to database...")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            print("Checking and migrating database...")
            
            # 1. Bookings table
            try:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS commission_amount FLOAT DEFAULT 0.0"))
                conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS provider_amount FLOAT DEFAULT 0.0"))
                conn.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS refund_status VARCHAR"))
                print("Bookings table columns verified/added.")
            except Exception as e:
                print(f"Bookings migration note: {e}")

            # 2. Complaints table
            try:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'pending'"))
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS resolution TEXT"))
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_notes TEXT"))
                print("Complaints table columns verified/added.")
            except Exception as e:
                print(f"Complaints migration note: {e}")

            # 3. Inquiries table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS inquiries (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR,
                        email VARCHAR,
                        phone VARCHAR,
                        subject VARCHAR,
                        message TEXT,
                        status VARCHAR DEFAULT 'new',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                print("Inquiries table verified/created.")
            except Exception as e:
                print(f"Inquiries migration note: {e}")

            conn.commit()
            print("Migration complete!")
    except Exception as e:
        print(f"FATAL: Database connection failed: {e}")

if __name__ == "__main__":
    migrate()
