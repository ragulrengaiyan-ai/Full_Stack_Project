from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Provider, Booking

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def admin_stats(db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    providers_count = db.query(Provider).count()
    bookings_count = db.query(Booking).count()
    
    # Calculate revenue
    try:
        from sqlalchemy import func
        total_sales = db.query(func.sum(Booking.total_amount)).filter(Booking.status == 'completed').scalar() or 0.0
        platform_revenue = db.query(func.sum(Booking.commission_amount)).filter(Booking.status == 'completed').scalar() or 0.0
    except Exception as e:
        # Fallback if columns missing or other DB error
        print(f"Error calculating revenue: {e}")
        total_sales = 0.0
        platform_revenue = 0.0

    return {
        "users": users_count,
        "providers": providers_count,
        "bookings": bookings_count,
        "total_sales": total_sales,
        "platform_revenue": platform_revenue
    }

from sqlalchemy.orm import joinedload

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).options(joinedload(User.provider_profile)).order_by(User.created_at.desc()).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.get("/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()
