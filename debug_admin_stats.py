import sys
import os
from dotenv import load_dotenv

load_dotenv()
from sqlalchemy import func

# Add project root to path
sys.path.append(os.getcwd())

from backend.app.database import SessionLocal
from backend.app.models import User, Provider, Booking

def test_admin_stats():
    db = SessionLocal()
    try:
        print("Testing User count...")
        users_count = db.query(User).count()
        print(f"Users: {users_count}")

        print("Testing Provider count...")
        providers_count = db.query(Provider).count()
        print(f"Providers: {providers_count}")

        print("Testing Booking count...")
        bookings_count = db.query(Booking).count()
        print(f"Bookings: {bookings_count}")
        
        print("Testing Revenue...")
        try:
            total_sales = db.query(func.sum(Booking.total_amount)).filter(Booking.status == 'completed').scalar() or 0.0
            print(f"Total Sales: {total_sales}")
            
            platform_revenue = db.query(func.sum(Booking.commission_amount)).filter(Booking.status == 'completed').scalar() or 0.0
            print(f"Platform Revenue: {platform_revenue}")
        except Exception as rev_err:
            print(f"Revenue calc error: {rev_err}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_stats()
