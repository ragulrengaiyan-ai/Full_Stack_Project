from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
import os
import sys
from pathlib import Path

# VERCEL-SAFE IMPORT LOGIC
# Ensure the backend/app directory is in sys.path so we can do flat imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from .database import engine, get_db, Base
    from .routes import users, services, providers, bookings, admin, complaints, reviews, inquiries
    from . import models, auth

except (ImportError, ValueError):
    # Fallback for Vercel if relative imports fail
    import database
    from database import engine, get_db, Base
    import routes.users as users
    import routes.services as services
    import routes.providers as providers
    import routes.bookings as bookings
    import routes.admin as admin
    import routes.complaints as complaints
    import routes.reviews as reviews
    import routes.inquiries as inquiries
    import models, auth


# Create tables and seed admin
try:
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed admin if database is empty or admin missing
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        admin_email = "admin@allinone.com"
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_user:
            print(f"AUTO-SEED: Creating default admin {admin_email}")
            new_admin = models.User(
                name="System Admin",
                email=admin_email,
                password=auth.generate_password_hash("admin123"),
                role="admin",
                phone="0000000000"
            )
            db.add(new_admin)
            db.commit()
    finally:
        db.close()
        
except Exception as e:
    print(f"Database sync/seed failed: {e}")

app = FastAPI(
    title="Urban Company Style API",
    description="Full Stack Household Services Application",
    version="1.3.2"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Simplified for the single-origin unified deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root level API routes
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(services.router, prefix="/api", tags=["Services"])
app.include_router(providers.router, prefix="/api", tags=["Providers"])
app.include_router(bookings.router, prefix="/api", tags=["Bookings"])
app.include_router(admin.router, prefix="/api", tags=["Admin"])
app.include_router(complaints.router, prefix="/api", tags=["Complaints"])
app.include_router(reviews.router, prefix="/api", tags=["Reviews"])
app.include_router(inquiries.router, prefix="/api", tags=["Inquiries"])

# Static Files Hosting (Professional Single-Origin Solution)
# Frontend is now located inside the app package for guaranteed Vercel bundling
frontend_path = Path(__file__).parent / "frontend"

if frontend_path.exists():
    # Mount subdirectories
    for folder in ["js", "css", "assets"]:
        target = frontend_path / folder
        if target.exists():
            app.mount(f"/{folder}", StaticFiles(directory=str(target)), name=folder)
    
    # Root index.html handler
    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_path / "index.html"))
    
    # Catch-all for HTML files and assets at the root of frontend/
    @app.get("/{path:path}")
    async def serve_static_html(path: str):
        file_path = frontend_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Default back to index
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "Backend running on Vercel - v1.3.1 (Frontend directory missing in bundle)"}
