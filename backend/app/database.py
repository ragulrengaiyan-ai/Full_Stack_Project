import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# CRITICAL: PRODUCTION DATABASE CONFIGURATION
# --------------------------------------------
# We strictly read from Environment Variables.
# No fallback to localhost or hardcoded credentials.
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # This error will appear in Vercel logs if the variable is missing.
    raise ValueError("FATAL: DATABASE_URL environment variable is not set.")

# SQLAlchemy requires 'postgresql://', but some providers give 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for DB session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
