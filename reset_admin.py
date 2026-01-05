from app.database import SessionLocal
from app.models import User

def reset_admin():
    db = SessionLocal()
    email = "admin@allinone.com"
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        user.password = "adminpassword"
        db.commit()
        print(f"Admin password for {email} has been reset to 'adminpassword'")
    else:
        print("Admin user not found. Creating new...")
        new_admin = User(
            name="System Admin",
            email="admin@allinone.com",
            phone="0000000000",
            password="adminpassword",
            role="admin"
        )
        db.add(new_admin)
        db.commit()
        print("New admin created with password 'adminpassword'")
    db.close()

if __name__ == "__main__":
    reset_admin()
