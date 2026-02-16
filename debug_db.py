import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload

# Add current dir to path for imports
sys.path.append(str(Path(__file__).parent / "backend" / "app"))

from database import engine
from models import Provider, User
from sqlalchemy.orm import Session

db = Session(bind=engine)
try:
    print("Connecting to database...")
    
    all_p = db.query(Provider).options(joinedload(Provider.user)).all()
    print(f"Total Providers: {len(all_p)}")
    
    print("\n--- Full Alignment Audit ---")
    for p in all_p:
        uname = p.user.name if p.user else "N/A"
        print(f"ID:{p.id} | Name:{uname} | Service:'{p.service_type}' | Loc:'{p.location}' | Addr:'{p.address}'")
    
finally:
    db.close()
