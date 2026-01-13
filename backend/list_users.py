import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add app directory to sys.path
app_path = Path(__file__).parent / "app"
sys.path.append(str(app_path))

try:
    from app.database import SessionLocal
    from app.models import User
except ImportError:
    from database import SessionLocal
    from models import User

def list_users():
    print(f"DEBUG: DATABASE_URL is {os.environ.get('DATABASE_URL')}")
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"DEBUG: Total users found: {len(users)}")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Role':<15}")
        print("-" * 70)
        for u in users:
            print(f"{u.id:<5} {u.name:<20} {u.email:<30} {u.role:<15}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
