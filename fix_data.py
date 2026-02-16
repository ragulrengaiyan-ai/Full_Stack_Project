import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current dir to path for imports
sys.path.append(str(Path(__file__).parent / "backend" / "app"))

from database import engine
from models import Provider, User
from sqlalchemy.orm import Session

db = Session(bind=engine)
try:
    print("Starting data fix...")
    
    # List of known cities to look for in the address field
    cities = ["Madurai", "Coimbatore", "Nagapattinam", "Thiruvarur", "Rameshwaram", "Vellore", "Thenkasi", "Chennai"]
    
    # Find providers who have location='Chennai' but might be elsewhere
    providers = db.query(Provider).all()
    
    updated_count = 0
    for p in providers:
        original_loc = p.location
        # If address is more specific or different, try to refine location
        found_city = None
        for city in cities:
            if p.address and city.lower() in p.address.lower():
                found_city = city
                break
        
        if found_city and p.location != found_city:
            print(f"Updating ID:{p.id} Name:{p.user.name if p.user else 'N/A'}")
            print(f"  Old Loc: '{p.location}' | Address: '{p.address}'")
            print(f"  New Loc: '{found_city}'")
            p.location = found_city
            updated_count += 1
            
    db.commit()
    print(f"\nSuccessfully updated {updated_count} providers.")
    
finally:
    db.close()
