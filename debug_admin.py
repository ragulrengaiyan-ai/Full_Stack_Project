from app.database import SessionLocal
from app.models import User

def check_admin():
    db = SessionLocal()
    email = "admin@allinone.com"
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        print(f"Admin Found: ID={user.id}, Email={user.email}, Role={user.role}, Password='{user.password}'")
    else:
        print("Admin NOT found.")
    db.close()

if __name__ == "__main__":
    check_admin()
