from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

try:
    from ..database import get_db
    from ..models import User, Provider, Booking, Review, Complaint
except (ImportError, ValueError):
    from database import get_db
    from models import User, Provider, Booking, Review, Complaint

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
def admin_stats(db: Session = Depends(get_db)):
    try:
        # Diagnostic counts
        users_count = db.query(User).count()
        providers_count = db.query(Provider).count()
        bookings_count = db.query(Booking).count()
        
        # Log counts for backend visibility
        print(f"STATS SYNC CHECK: Users={users_count}, Providers={providers_count}, Bookings={bookings_count}")
        
        # Revenue calculation
        total_sales = 0.0
        platform_revenue = 0.0
        
        try:
            total_sales_raw = db.query(func.sum(Booking.total_amount)).filter(Booking.status == 'completed').scalar()
            total_sales = float(total_sales_raw) if total_sales_raw else 0.0
        except Exception as sales_err:
            print(f"Sales calculation failed: {sales_err}")

        try:
            platform_revenue_raw = db.query(func.sum(Booking.commission_amount)).filter(Booking.status == 'completed').scalar()
            platform_revenue = float(platform_revenue_raw) if platform_revenue_raw else 0.0
        except Exception as rev_err:
            print(f"Revenue calculation failed: {rev_err}")

        return {
            "users": users_count,
            "providers": providers_count,
            "bookings": bookings_count,
            "total_sales": total_sales,
            "platform_revenue": platform_revenue,
            "status": "success"
        }
    except Exception as e:
        print(f"CRITICAL STATS ERROR: {e}")
        return {
            "users": 0,
            "providers": 0,
            "bookings": 0,
            "total_sales": 0.0,
            "platform_revenue": 0.0,
            "status": "failure",
            "error": str(e)
        }

from sqlalchemy.orm import joinedload

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    try:
        data = db.query(User).options(joinedload(User.provider_profile)).order_by(User.created_at.desc()).all()
        print(f"Fetched {len(data)} users for admin list")
        return data
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"ADM ALERT: Manually deleting user {user_id} and all related data to bypass DB constraints")

        # 1. Handle Provider Profile and dependency chain
        provider = db.query(Provider).filter(Provider.user_id == user_id).first()
        if provider:
            # Delete everything linked to provider's bookings
            p_booking_ids = [b.id for b in db.query(Booking.id).filter(Booking.provider_id == provider.id).all()]
            if p_booking_ids:
                db.query(Review).filter(Review.booking_id.in_(p_booking_ids)).delete(synchronize_session=False)
                db.query(Complaint).filter(Complaint.booking_id.in_(p_booking_ids)).delete(synchronize_session=False)
                db.query(Booking).filter(Booking.id.in_(p_booking_ids)).delete(synchronize_session=False)
            
            # Delete provider reviews directly
            db.query(Review).filter(Review.provider_id == provider.id).delete(synchronize_session=False)
            db.delete(provider)
        
        # 2. Handle Customer activity
        db.query(Review).filter(Review.customer_id == user_id).delete(synchronize_session=False)
        db.query(Complaint).filter(Complaint.customer_id == user_id).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.customer_id == user_id).delete(synchronize_session=False)
        
        # 3. Final User Deletion
        db.delete(user)
        db.commit()
        print(f"ADM SUCCESS: User {user_id} completely removed")
        return {"message": "User and all related data deleted successfully"}
    except Exception as e:
        db.rollback()
        print(f"CRITICAL DELETE ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Database deletion failed: {str(e)}")

@router.get("/bookings")
def get_all_bookings(db: Session = Depends(get_db)):
    try:
        return db.query(Booking).all()
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return []
