from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Provider, Booking

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def admin_stats(db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    providers_count = db.query(Provider).count()
    bookings_count = db.query(Booking).count()
    return {
        "users": users_count,
        "providers": providers_count,
        "bookings": bookings_count
    }

from sqlalchemy.orm import joinedload

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).options(joinedload(User.provider_profile)).all()

@router.get("/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
