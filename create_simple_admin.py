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
from passlib.context import CryptContext

# Create a simple bcrypt context
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_simple_admin():
    print(f"Using Database: {os.environ.get('DATABASE_URL')[:20] if os.environ.get('DATABASE_URL') else 'NONE'}...")
    
    db = SessionLocal()
    
    # Delete existing admin if exists
    existing_admin = db.query(User).filter(User.email == "admin@allinone.com").first()
    if existing_admin:
        db.delete(existing_admin)
        db.commit()
        print("Deleted existing admin user")
    
    # Create new admin with simple bcrypt hash
    simple_password = "admin123"
    hashed = bcrypt_context.hash(simple_password)
    
    admin_user = User(
        name="Admin User",
        email="admin@allinone.com",
        phone="0000000000",
        password=hashed,
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    
    print(f"\n✅ NEW Admin account created!")
    print(f"   Email: admin@allinone.com")
    print(f"   Password: {simple_password}")
    print(f"   Hash type: bcrypt")
    print(f"\nTry logging in with these NEW credentials!")
    
    db.close()

if __name__ == "__main__":
    create_simple_admin()
