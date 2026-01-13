
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

try:
    from ..database import get_db
    from ..auth import get_current_user, get_current_user_optional
    from ..schemas import ProviderOut, UserOut
    from ..models import Provider, Review, User
except (ImportError, ValueError):
    from database import get_db
    from auth import get_current_user, get_current_user_optional
    from schemas import ProviderOut, UserOut
    from models import Provider, Review, User

router = APIRouter(prefix="/providers", tags=["Providers"])


from sqlalchemy.orm import joinedload

@router.get("/", response_model=List[ProviderOut])
def get_providers(
    service_type: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_experience: Optional[int] = None,
    availability_status: Optional[str] = "available",
    booking_date: Optional[str] = None, # YYYY-MM-DD
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Provider).options(joinedload(Provider.user)).filter(Provider.background_verified == "verified")

    if booking_date:
        # Exclude providers who have a booking on this date
        # This implementation assumes one booking per day for simplicity of 'day-wise' requirement
        try:
            from ..models import Booking
        except (ImportError, ValueError):
            from models import Booking
        booked_provider_ids = db.query(Booking.provider_id).filter(
            Booking.booking_date == booking_date,
            Booking.status.in_(["pending", "confirmed"])
        ).all()
        ids = [i[0] for i in booked_provider_ids]
        query = query.filter(~Provider.id.in_(ids))

    if service_type:
        query = query.filter(Provider.service_type == service_type)

    if location:
        query = query.filter(or_(
            Provider.location.ilike(f"%{location}%"),
            Provider.address.ilike(f"%{location}%")
        ))

    if min_rating:
        query = query.filter(Provider.rating >= min_rating)

    if min_price is not None:
        query = query.filter(Provider.hourly_rate >= min_price)
    
    if max_price is not None:
        query = query.filter(Provider.hourly_rate <= max_price)

    if min_experience is not None:
        query = query.filter(Provider.experience_years >= min_experience)

    if availability_status:
        query = query.filter(Provider.availability_status == availability_status)

    # Sorting
    if sort_by == "rating":
        query = query.order_by(Provider.rating.desc())
    elif sort_by == "price_low":
        query = query.order_by(Provider.hourly_rate.asc())
    elif sort_by == "price_high":
        query = query.order_by(Provider.hourly_rate.desc())
    elif sort_by == "experience":
        query = query.order_by(Provider.experience_years.desc())
    else:
        # Default sort by rating
        query = query.order_by(Provider.rating.desc())

    return query.all()


@router.get("/profile/{user_id}", response_model=ProviderOut)
def get_provider_by_user_id(user_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.user_id == user_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider profile not found for this user")
    return provider


@router.get("/{provider_id}", response_model=ProviderOut)
def get_provider_details(
    provider_id: int, 
    admin_review: Optional[bool] = False, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Secure Admin Bypass
    is_admin = current_user and current_user.role == "admin"
    allow_bypass = admin_review and is_admin
    
    
    if provider.background_verified != "verified" and not allow_bypass:
        raise HTTPException(status_code=404, detail="Provider not found or not yet verified")

    return provider


@router.get("/service/{service_type}", response_model=List[ProviderOut])
def get_providers_by_service(service_type: str, db: Session = Depends(get_db)):
    return db.query(Provider).filter(
        Provider.service_type == service_type,
        Provider.availability_status == "available",
        Provider.background_verified == "verified"
    ).all()


@router.patch("/{provider_id}/verify")
def verify_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider.background_verified = "verified"
    db.commit()
    return {"message": "Provider verified successfully"}

