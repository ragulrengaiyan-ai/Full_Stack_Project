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

        query = query.filter(or_(
            Provider.location.ilike(f"%{location}%"),
            Provider.address.ilike(f"%{location}%")
        ))
        print(f"Applied location filter: {location}")
        # Print the SQL
        from sqlalchemy.dialects import postgresql
        print("GENERATED SQL:")
        print(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))

    results = query.all()
    print(f"Match count: {len(results)}")
    for p in results:
        user = db.query(User).filter(User.id == p.user_id).first()
        uname = user.name if user else "Unknown"
        loc_match = False
        addr_match = False
        if location:
            loc_match = location.lower() in (p.location or "").lower()
            addr_match = location.lower() in (p.address or "").lower()
        
        print(f"MATCH: [{p.id}] {uname}")
        print(f"  - DB Loc: '{p.location}' (Python Match: {loc_match})")
        print(f"  - DB Addr: '{p.address}' (Python Match: {addr_match})")
        print(f"  - Service: '{p.service_type}'")

test_production_logic('babysitter', 'chennai')
test_production_logic('babysitter', None)

db.close()
