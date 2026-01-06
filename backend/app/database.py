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

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# SQLAlchemy requires 'postgresql://', but some providers give 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# CRITICAL: Robustly strip 'channel_binding' which causes psycopg2 errors on Vercel
try:
    u = urlparse(DATABASE_URL)
    query = parse_qs(u.query)
    # Remove channel_binding if present
    query.pop('channel_binding', None)
    # Rebuild URL
    u = u._replace(query=urlencode(query, doseq=True))
    DATABASE_URL = urlunparse(u).strip("'").strip('"').strip()
except Exception:
    pass # Fallback to original if parsing fails

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
