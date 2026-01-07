from dotenv import load_dotenv
import os
import sys

# Load .env file at the very beginning
load_dotenv()

# Add backend to sys.path if not already there
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.database import SessionLocal
from app.models import User

def check_admin():
    print(f"Using Database: {os.environ.get('DATABASE_URL')[:20] if os.environ.get('DATABASE_URL') else 'NONE'}...")
    
    db = SessionLocal()
    
    # Find admin user
    admin = db.query(User).filter(User.email == "admin@allinone.com").first()
    
    if admin:
        print(f"\n✅ Admin user found!")
        print(f"   ID: {admin.id}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Password hash (first 50 chars): {admin.password[:50]}...")
        print(f"   Hash scheme: {'pbkdf2_sha256' if admin.password.startswith('$pbkdf2') else 'bcrypt' if admin.password.startswith('$2b$') else 'unknown'}")
    else:
        print("❌ Admin user NOT found in database!")
    
    db.close()

if __name__ == "__main__":
    check_admin()
