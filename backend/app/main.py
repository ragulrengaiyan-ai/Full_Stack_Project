from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from .database import engine, get_db, Base
from .routes import users, services, providers, bookings, admin, complaints, reviews, inquiries
from . import models, auth

# Create tables
# In production with Vercel/Neon, we usually do this via migrations,
# but for this setup, we'll ensure they exist.
try:
    models.Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database sync skipped/failed during build: {e}")

app = FastAPI(
    title="Urban Company Style API",
    description="Full Stack Household Services Application",
    version="1.2.0"
)

# CORS Configuration
# Standardizing origins to include the Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://all-in-one-household-services.netlify.app",
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

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend running on Vercel - v1.2.0 (Professional Workflow Active)"}
