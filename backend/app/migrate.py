from sqlalchemy import text
from .database import engine

def run_db_migrations():
    """
    Manually add columns that were added to the models but are missing 
    in the production database.
    """
    sql_commands = [
        # Bookings table updates
        "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS refund_status VARCHAR",
        "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS commission_amount FLOAT DEFAULT 0.0",
        "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS provider_amount FLOAT DEFAULT 0.0",
        
        # Providers table updates
        "ALTER TABLE providers ADD COLUMN IF NOT EXISTS earnings FLOAT DEFAULT 0.0",
        
        # Ensure status columns have proper defaults if they were null
        "UPDATE bookings SET status = 'pending' WHERE status IS NULL",
        "UPDATE providers SET background_verified = 'pending' WHERE background_verified IS NULL"
    ]
    
    results = []
    with engine.connect() as conn:
        for cmd in sql_commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                results.append(f"SUCCESS: {cmd}")
            except Exception as e:
                results.append(f"FAILED: {cmd} | Error: {str(e)}")
    
    return results
