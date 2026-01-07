from dotenv import load_dotenv
import os
import sys
import hashlib

# Load .env file at the very beginning
load_dotenv()

# Add backend to sys.path if not already there
backend_path = os.path.join(os.getcwd(), "backend")
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.database import SessionLocal
from app.models import User

def create_test_admin():
    print(f"Using Database: {os.environ.get('DATABASE_URL')[:20] if os.environ.get('DATABASE_URL') else 'NONE'}...")
    
    db = SessionLocal()
    
    # Delete existing admin if exists
    existing_admin = db.query(User).filter(User.email == "test@admin.com").first()
    if existing_admin:
        db.delete(existing_admin)
        db.commit()
        print("Deleted existing test admin")
    
    # Create a VERY simple password hash using pbkdf2_sha256 manually
    # This matches what passlib generates
    password = "test123"
    from passlib.hash import pbkdf2_sha256
    hashed = pbkdf2_sha256.hash(password)
    
    admin_user = User(
        name="Test Admin",
        email="test@admin.com",
        phone="1111111111",
        password=hashed,
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    
    print(f"\n✅ TEST Admin account created!")
    print(f"   Email: test@admin.com")
    print(f"   Password: {password}")
    print(f"   Hash: {hashed[:50]}...")
    print(f"\nTry logging in with these credentials!")
    
    db.close()

if __name__ == "__main__":
    create_test_admin()
