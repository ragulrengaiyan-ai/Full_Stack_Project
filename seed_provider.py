from app.database import SessionLocal
from app.models import User, Provider

def seed_provider():
    db = SessionLocal()
    try:
        email = "supercook@test.com"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("User already exists.")
            return

        # Create User
        new_user = User(
            name="Super Cook",
            email=email,
            phone="9876543210",
            password="password123", # Plain text for simple mode
            role="provider"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create Provider Profile
        new_provider = Provider(
            user_id=new_user.id,
            service_type="Cook",
            experience_years=5,
            hourly_rate=500.0,
            location="Chennai",
            bio="Expert in South Indian cuisine.",
            availability_status="available",
            background_verified="pending" # Admin can verify later
        )
        db.add(new_provider)
        db.commit()
        
        print(f"Successfully created provider: {email} / password123")

    except Exception as e:
        print(f"Error seeding provider: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_provider()
