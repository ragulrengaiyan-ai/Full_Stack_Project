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
    print(f"{'ID':<4} | {'Name':<15} | {'Service':<12} | {'Loc':<15} | {'Status':<10} | {'Verified':<10}")
    print("-" * 80)
    for p in all_p:
        uname = p.user.name if p.user else "N/A"
        print(f"{p.id:<4} | {uname:<15} | {p.service_type:<12} | {p.location:<15} | {p.availability_status:<10} | {p.background_verified:<10}")
    
finally:
    db.close()
