from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path

from .database import engine, get_db, Base
from .routes import users, services, providers, bookings, admin, complaints, reviews, inquiries
from . import models, auth

# Create tables
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database sync skipped/failed during build: {e}")

app = FastAPI(
    title="Urban Company Style API",
    description="Full Stack Household Services Application",
    version="1.3.1"
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
    for folder in ["js", "css", "csspages", "htmlpages", "assets"]:
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
