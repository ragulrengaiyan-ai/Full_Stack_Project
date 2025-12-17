from app.database import SessionLocal
from app.models import User

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.email == "admin@allinone.com").first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # Create new admin
        new_admin = User(
            name="System Admin",
            email="admin@allinone.com",
            phone="0000000000",
            password="adminpassword", # In production, hash this!
            role="admin"
        )
        db.add(new_admin)
        db.commit()
        print("Admin user created successfully!")
        print("Email: admin@allinone.com")
        print("Password: adminpassword")
    
    except Exception as e:
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
