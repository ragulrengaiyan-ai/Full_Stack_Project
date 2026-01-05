
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user, get_current_user_optional
from app.schemas import ProviderOut, UserOut
from app.models import Provider, Review, User

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/", response_model=List[ProviderOut])
def get_providers(
    service_type: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_experience: Optional[int] = None,
    availability_status: Optional[str] = "available",
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Provider).filter(Provider.background_verified == "verified")

    if service_type:
        query = query.filter(Provider.service_type == service_type)

    if location:
        query = query.filter(Provider.location.ilike(f"%{location}%"))

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

