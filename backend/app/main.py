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
    version="1.3.0"
)

# CORS Configuration
# Standardizing origins - including the same-origin for unified hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://all-in-one-household-services.netlify.app",
        "https://full-stack-project-iota-lime.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
    ],
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

# Static Files Hosting (Unified Vercel Solution)
# Assuming frontend is at the same level as backend in the repo root
# Vercel structure: /backend/app/main.py -> frontend is at /frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"

if frontend_path.exists():
    # Mount all subdirectories (JS, CSS, HTMLPages, etc.)
    app.mount("/js", StaticFiles(directory=str(frontend_path / "js")), name="js")
    app.mount("/css", StaticFiles(directory=str(frontend_path / "css")), name="css")
    app.mount("/csspages", StaticFiles(directory=str(frontend_path / "csspages")), name="csspages")
    app.mount("/htmlpages", StaticFiles(directory=str(frontend_path / "htmlpages")), name="htmlpages")
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    
    # Root index.html handler
    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_path / "index.html"))
    
    # Catch-all for other root level HTML files (about.html, login.html, etc.)
    @app.get("/{path:path}")
    async def serve_static_html(path: str):
        file_path = frontend_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # Default back to index for SPA or if not found
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"status": "ok", "message": "Backend running on Vercel - v1.3.0 (Frontend path not found)"}
