from app.database import SessionLocal
from app.models import User, Provider

def check_user():
    db = SessionLocal()
    email = "supercook@test.com"
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        print(f"User Found: ID={user.id}, Name={user.name}, Role={user.role}, Password={user.password}")
        provider = db.query(Provider).filter(Provider.user_id == user.id).first()
        if provider:
             print(f"Provider Profile Found: ID={provider.id}, Service={provider.service_type}")
        else:
             print("NO Provider Profile found!")
    else:
        print("User NOT found in database.")
    
    db.close()

if __name__ == "__main__":
    check_user()
