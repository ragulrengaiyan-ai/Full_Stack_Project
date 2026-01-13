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

# Ensure required libraries are imported
try:
    from app.database import SessionLocal
    from app.models import User
    from app.auth import generate_password_hash
except ImportError:
    # Fallback for different path configurations
    import database
    from database import SessionLocal
    import models
    from models import User
    import auth
    from auth import generate_password_hash

def seed_accounts():
    db = SessionLocal()
    try:
        # 1. Setup Admin Account
        admin_email = "admin@allinone.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if admin:
            print(f"Updating Admin {admin_email} password to 'admin123'...")
            admin.password = generate_password_hash("admin123")
            admin.role = "admin"
        else:
            print(f"Creating Admin {admin_email}...")
            admin = User(
                name="System Admin",
                email=admin_email,
                password=generate_password_hash("admin123"),
                role="admin",
                phone="0000000000"
            )
            db.add(admin)
        
        # 2. Revert/Setup User Account
        user_email = "ragul@allinone.com"
        user = db.query(User).filter(User.email == user_email).first()
        if user:
            print(f"Reverting {user_email} to customer role and setting password to 'ragul@123'...")
            user.password = generate_password_hash("ragul@123")
            user.role = "customer"
        else:
            print(f"Creating User {user_email}...")
            user = User(
                name="Ragul Rengaiyan",
                email=user_email,
                password=generate_password_hash("ragul@123"),
                role="customer",
                phone="9876543210"
            )
            db.add(user)
            
        db.commit()
        print("Success: Admin is admin@allinone.com (admin123), User is ragul@allinone.com (ragul@123)")
            
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_accounts()
