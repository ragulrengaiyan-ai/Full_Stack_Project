from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

from app.database import Base, engine
from app.routes import users, services, bookings, admin, providers, reviews

# ========================
# BASE DIRECTORY SETUP
# backend/app/main.py -> backend
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="All In One API")

# ========================
# CORS
# ========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# STATIC FILES
# backend/static
# ========================
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    os.makedirs(static_dir)

app.mount(
    "/static",
    StaticFiles(directory=static_dir),
    name="static"
)

# ========================
# DB
# ========================
Base.metadata.create_all(bind=engine)

# ========================
# ROUTERS
# ========================
app.include_router(users.router)
app.include_router(providers.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(reviews.router)

# ========================
# HOME PAGE
# ========================
@app.get("/", response_class=HTMLResponse)
def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>Frontend not found</h1>"
