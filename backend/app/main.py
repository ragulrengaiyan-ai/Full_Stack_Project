from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import api, users, services, providers, bookings, admin, complaints, reviews

# Create tables on startup (Simple approach for this scaffold)
# Note: In a real project with changes to models, you should use migrations (Alembic).
# For now, tables are created automatically on Vercel startup.
Base.metadata.create_all(bind=engine)

# Ensure Admin User exists and has correct role (One-time setup for prod)
from .database import SessionLocal
from .models import User
from .auth import generate_password_hash

def init_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@allinone.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if admin:
            # Always ensure correct role and password for this specific user
            admin.role = "admin"
            # Refresh password to the new one we set
            admin.password = generate_password_hash("admin_allinone_2026")
            db.commit()
            print(f"Admin role/password synchronized: {admin_email}")
        else:
            # Create if missing
            new_admin = User(
                name="Admin User",
                email=admin_email,
                phone="0000000000",
                password=generate_password_hash("admin_allinone_2026"),
                role="admin"
            )
            db.add(new_admin)
            db.commit()
            print(f"Admin account created on startup: {admin_email}")
    except Exception as e:
        print(f"Error initializing admin: {e}")
    finally:
        db.close()

init_admin()

app = FastAPI(
    title="Urban Company Style API",
    description="Full Stack Household Services Application",
    version="1.1.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api", tags=["Tests"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(services.router, prefix="/api", tags=["Services"])
app.include_router(providers.router, prefix="/api", tags=["Providers"])
app.include_router(bookings.router, prefix="/api", tags=["Bookings"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(complaints.router, prefix="/api", tags=["Complaints"])
app.include_router(reviews.router, prefix="/api", tags=["Reviews"])

@app.get("/")
def read_root():
    # Force redeploy - 2026-01-07
    return {"status": "ok", "message": "Backend running on Vercel"}
