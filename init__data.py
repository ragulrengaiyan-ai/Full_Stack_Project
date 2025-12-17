from app.database import SessionLocal
from app.models import User, Provider, Service
from app.auth import generate_password_hash

def init_sample_data():
    db = SessionLocal()
    
    # Create sample services
    services = [
        Service(name="babysitter", description="Professional childcare", base_price=350, category="household"),
        Service(name="cook", description="Home cooking services", base_price=450, category="household"),
        Service(name="housekeeper", description="Cleaning services", base_price=400, category="household"),
        Service(name="gardener", description="Garden maintenance", base_price=300, category="outdoor"),
        Service(name="security", description="Security services", base_price=500, category="safety"),
    ]
    
    for service in services:
        existing = db.query(Service).filter(Service.name == service.name).first()
        if not existing:
            db.add(service)
    
    # Create sample providers
    providers_data = [
        {
            "name": "Sarah Johnson",
            "email": "sarah@example.com",
            "phone": "9876543210",
            "service_type": "babysitter",
            "experience_years": 5,
            "hourly_rate": 16.0,
            "location": "Downtown Chennai",
            "bio": "Experienced babysitter with 5 years of experience"
        },
        {
            "name": "Nagarjun Kumar",
            "email": "naga@example.com",
            "phone": "9876543211",
            "service_type": "cook",
            "experience_years": 7,
            "hourly_rate": 18.0,
            "location": "T Nagar Chennai",
            "bio": "Professional chef specializing in South Indian cuisine"
        },
        {
            "name": "Maria Garcia",
            "email": "maria@example.com",
            "phone": "9876543212",
            "service_type": "housekeeper",
            "experience_years": 4,
            "hourly_rate": 14.0,
            "location": "Velachery Chennai",
            "bio": "Thorough and reliable housekeeper"
        },
    ]
    
    for provider_data in providers_data:
        existing = db.query(User).filter(User.email == provider_data["email"]).first()
        if not existing:
            # Create user
            user = User(
                name=provider_data["name"],
                email=provider_data["email"],
                phone=provider_data["phone"],
                password=generate_password_hash("password123"),
                role="provider"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create provider profile
            provider = Provider(
                user_id=user.id,
                service_type=provider_data["service_type"],
                experience_years=provider_data["experience_years"],
                hourly_rate=provider_data["hourly_rate"],
                location=provider_data["location"],
                bio=provider_data["bio"],
                rating=4.8,
                total_bookings=50,
                availability_status="available",
                background_verified="verified"
            )
            db.add(provider)
    
    db.commit()
    print("Sample data initialized successfully!")
    db.close()

if __name__ == "__main__":
    init_sample_data()