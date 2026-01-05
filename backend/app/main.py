from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

from app.database import Base, engine
from app.routes import users, services, bookings, admin, providers, reviews, complaints



BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="All In One API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


static_dir = BASE_DIR.parent / "frontend"
if not static_dir.exists():
    os.makedirs(static_dir)

app.mount("/js", StaticFiles(directory=static_dir / "js"), name="js")
app.mount("/csspages", StaticFiles(directory=static_dir / "csspages"), name="csspages")
app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

# Serve general static files (like style.css) from frontend root
app.mount("/static", StaticFiles(directory=static_dir), name="static")

Base.metadata.create_all(bind=engine)


app.include_router(users.router)
app.include_router(providers.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(admin.router)
app.include_router(complaints.router)
app.include_router(reviews.router)



@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return index_file.read_text(encoding="utf-8")
    return "<h1>Frontend index.html not found</h1>"

@app.get("/{page_name}.html", response_class=HTMLResponse)
def serve_html_page(page_name: str):
    # Try root first
    file_path = static_dir / f"{page_name}.html"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    
    # Try htmlpages subdirectory
    file_path = static_dir / "htmlpages" / f"{page_name}.html"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    
    raise HTTPException(status_code=404, detail=f"Page {page_name}.html not found")

@app.get("/htmlpages/{page_name}.html", response_class=HTMLResponse)
def serve_html_subdir_page(page_name: str):
    file_path = static_dir / "htmlpages" / f"{page_name}.html"
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail=f"Page {page_name}.html not found in htmlpages")
