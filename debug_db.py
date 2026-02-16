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
    
    print("\n--- Searching for Prakash and Sulaiman ---")
    specific_providers = db.query(Provider).join(User).filter(User.name.in_(["Prakash", "Sulaiman"])).all()
    for p in specific_providers:
        user = db.query(User).filter(User.id == p.user_id).first()
        print(f"[{p.id}] {user.name} | Service: '{p.service_type}' | Loc: '{p.location}' | Addr: '{p.address}'")
    
    db.close()
except Exception as e:
    print(f"Error: {e}")
