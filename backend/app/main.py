from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import api, users, services, providers, bookings, admin, complaints, reviews

# Create tables on startup (Simple approach for this scaffold)
# Note: In a real project with changes to models, you should use migrations (Alembic).
# For now, tables are created automatically on Vercel startup.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Urban Company Style API",
    description="Full Stack Household Services Application",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    return {"status": "ok", "message": "Backend running on Vercel"}
