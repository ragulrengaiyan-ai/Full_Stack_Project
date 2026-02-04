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
    
    # Auto-seed admin: Force update password and role for guaranteed access
    from sqlalchemy.orm import Session
    db = Session(bind=engine)
    try:
        admin_email = "admin@allinone.com"
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        
        if admin_user:
            print(f"AUTO-SEED: Force updating existing admin {admin_email}")
            admin_user.password = auth.generate_password_hash("admin123")
            admin_user.role = "admin"
        else:
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

# SCHEMA MIGRATION: Auto-patch missing columns for 'complaints' table
# This handles the case where the table existed before the new columns were added.
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        with conn.begin(): # Start transaction
            # Add 'status' column if missing
            try:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS status VARCHAR DEFAULT 'pending'"))
            except Exception as e:
                print(f"Migration warning (status): {e}")

            # Add 'resolution' column if missing
            try:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS resolution TEXT"))
            except Exception as e:
                print(f"Migration warning (resolution): {e}")

            # Add 'admin_notes' column if missing
            try:
                conn.execute(text("ALTER TABLE complaints ADD COLUMN IF NOT EXISTS admin_notes TEXT"))
            except Exception as e:
                print(f"Migration warning (admin_notes): {e}")
                
            print("Schema migration for 'complaints' completed.")
except Exception as e:
     print(f"Schema migration failed: {e}")

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

# Global Exception Handler for better debugging
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    print(f"GLOBAL ERROR CAUGHT: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "type": type(exc).__name__}
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

# Static Files Hosting (Python-Served Frontend)
# Files are now bundled INSIDE the package at backend/app/static
# This guarantees availability in the Vercel Lambda environment.

static_path = Path(__file__).parent / "static"

# Mount the static directory to serve js, css, assets directly if requested via /static/
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Also mount specific folders to matching root paths for compatibility
for folder in ["js", "css", "assets"]:
    target = static_path / folder
    if target.exists():
        app.mount(f"/{folder}", StaticFiles(directory=str(target)), name=folder)

@app.get("/{path_name:path}")
async def catch_all(path_name: str):
    # API routes are already handled above. Everything else is frontend.
    
    # default to index.html for root
    if path_name == "" or path_name == "/":
        file_path = static_path / "index.html"
    else:
        file_path = static_path / path_name
        
        # If no extension, try adding .html (clean URLs support)
        if not file_path.suffix and not file_path.exists():
             file_path = static_path / f"{path_name}.html"

    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    
    # 404 for truly missing files
    return JSONResponse(
        {"error": "File not found", "path": path_name, "resolved": str(file_path)}, 
        status_code=404
    )

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend API is active", "version": "1.3.8"}
