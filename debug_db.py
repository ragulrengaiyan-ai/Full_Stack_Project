import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current dir to path for imports
sys.path.append(str(Path(__file__).parent / "backend" / "app"))

try:
    from database import engine
    from models import Provider, User
    from sqlalchemy.orm import Session
    
    db = Session(bind=engine)
    print("Connecting to database...")
    
    providers = db.query(Provider).all()
    print(f"Total Providers: {len(providers)}")
    
    print("\n--- Searching for Siddharth ---")
    siddharth = db.query(Provider).join(User).filter(User.name.ilike("%Siddharth%")).all()
    for p in siddharth:
        user = db.query(User).filter(User.id == p.user_id).first()
        print(f"ID:{p.id} | Name:{user.name} | Loc:'{p.location}' | Addr:'{p.address}'")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
