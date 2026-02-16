import os
import sys
from pathlib import Path
from sqlalchemy import or_
from sqlalchemy.orm import Session

# Add current dir to path for imports
sys.path.append(str(Path(__file__).parent / "backend" / "app"))

from database import engine
from models import Provider, User

db = Session(bind=engine)

def test_production_logic(service_type, location):
    print(f"\nTESTING: service_type='{service_type}', location='{location}'")
    query = db.query(Provider).filter(Provider.background_verified == "verified")
    
    if service_type:
        service_type = service_type.strip().lower()
        query = query.filter(Provider.service_type.ilike(f"{service_type}"))
        print(f"Applied service_type filter: {service_type}")

    if location:
        location = location.strip()
        query = query.filter(or_(
            Provider.location.ilike(f"%{location}%"),
            Provider.address.ilike(f"%{location}%")
        ))
        print(f"Applied location filter: {location}")

    results = query.all()
    print(f"Match count: {len(results)}")
    for p in results:
        user = db.query(User).filter(User.id == p.user_id).first()
        uname = user.name if user else "Unknown"
        print(f"MATCH: [{p.id}] {uname} | Loc:'{p.location}' | Addr:'{p.address}'")

test_production_logic('babysitter', 'chennai')
test_production_logic('babysitter', None)

db.close()
