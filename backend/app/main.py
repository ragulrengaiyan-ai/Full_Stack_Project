from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import api

# Create tables on startup (Simple approach for this scaffold)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Production Full Stack API",
    description="Vercel + Netlify + PostgreSQL",
    version="1.0.0"
)

# ---------------------------------------------------------
# CORS Configuration for Netlify
# ---------------------------------------------------------
origins = [
    "*", # Allow all for initial setup. Secure this to your Netlify domain in production!
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router, prefix="/api", tags=["items"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Backend running on Vercel"}
