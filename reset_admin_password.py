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
from app.auth import generate_password_hash

def reset_admin_password():
    print(f"Using Database: {os.environ.get('DATABASE_URL')[:20] if os.environ.get('DATABASE_URL') else 'NONE'}...")
    
    db = SessionLocal()
    
    # Find admin user
    admin = db.query(User).filter(User.email == "admin@allinone.com").first()
    
    if admin:
        # Reset password with new hash
        new_password = "admin_allinone_2026"
        admin.password = generate_password_hash(new_password)
        db.commit()
        print(f"✅ Admin password reset successfully!")
        print(f"   Email: admin@allinone.com")
        print(f"   Password: {new_password}")
    else:
        print("❌ Admin user not found. Creating new admin...")
        admin_user = User(
            name="Admin User",
            email="admin@allinone.com",
            phone="0000000000",
            password=generate_password_hash("admin_allinone_2026"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print(f"✅ Admin account created!")
        print(f"   Email: admin@allinone.com")
        print(f"   Password: admin_allinone_2026")
    
    db.close()

if __name__ == "__main__":
    reset_admin_password()
