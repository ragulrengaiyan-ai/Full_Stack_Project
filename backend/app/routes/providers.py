# # app/routes/providers.py
# from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from app.database import get_db
# from app.schemas import ProviderOut
# from app.models import Provider, User, Review

# router = APIRouter(prefix="/providers", tags=["Providers"])


# @router.get("/", response_model=List[ProviderOut])
# def get_providers(
#     service_type: Optional[str] = None,
#     location: Optional[str] = None,
#     min_rating: Optional[float] = None,
#     availability_status: Optional[str] = "available",
#     db: Session = Depends(get_db)
# ):
#     query = db.query(Provider).join(User)
    
#     if service_type:
#         query = query.filter(Provider.service_type == service_type)
#     if location:
#         query = query.filter(Provider.location.ilike(f"%{location}%"))
#     if min_rating:
#         query = query.filter(Provider.rating >= min_rating)
#     if availability_status:
#         query = query.filter(Provider.availability_status == availability_status)
    
#     providers = query.all()
#     return providers


# @router.get("/{provider_id}")
# def get_provider_details(provider_id: int, db: Session = Depends(get_db)):
#     provider = db.query(Provider).filter(Provider.id == provider_id).first()
#     if not provider:
#         raise HTTPException(status_code=404, detail="Provider not found")
    
#     # Get reviews
#     reviews = db.query(Review).filter(Review.provider_id == provider_id).all()
    
#     return {
#         "provider": {
#             "id": provider.id,
#             "name": provider.user.name,
#             "email": provider.user.email,
#             "phone": provider.user.phone,
#             "service_type": provider.service_type,
#             "experience_years": provider.experience_years,
#             "hourly_rate": provider.hourly_rate,
#             "location": provider.location,
#             "bio": provider.bio,
#             "rating": provider.rating,
#             "total_bookings": provider.total_bookings,
#             "availability_status": provider.availability_status,
#             "background_verified": provider.background_verified
#         },
#         "reviews": [
#             {
#                 "id": r.id,
#                 "rating": r.rating,
#                 "comment": r.comment,
#                 "created_at": r.created_at.strftime("%Y-%m-%d")
#             } for r in reviews
#         ]
#     }


# @router.get("/service/{service_type}", response_model=List[ProviderOut])
# def get_providers_by_service(service_type: str, db: Session = Depends(get_db)):
#     providers = db.query(Provider).filter(
#         Provider.service_type == service_type,
#         Provider.availability_status == "available"
#     ).all()
#     return providers


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import ProviderOut
from app.models import Provider, Review

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/", response_model=List[ProviderOut])
def get_providers(
    service_type: Optional[str] = None,
    location: Optional[str] = None,
    min_rating: Optional[float] = None,
    availability_status: Optional[str] = "available",
    db: Session = Depends(get_db)
):
    query = db.query(Provider)

    if service_type:
        query = query.filter(Provider.service_type == service_type)

    if location:
        query = query.filter(Provider.location.ilike(f"%{location}%"))

    if min_rating:
        query = query.filter(Provider.rating >= min_rating)

    if availability_status:
        query = query.filter(Provider.availability_status == availability_status)

    return query.all()


@router.get("/{provider_id}")
def get_provider_details(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    reviews = db.query(Review).filter(
        Review.provider_id == provider_id
    ).all()

    return {
        "provider": {
            "id": provider.id,
            "name": provider.user.name,
            "email": provider.user.email,
            "phone": provider.user.phone,
            "service_type": provider.service_type,
            "experience_years": provider.experience_years,
            "hourly_rate": provider.hourly_rate,
            "location": provider.location,
            "bio": provider.bio,
            "rating": provider.rating,
            "total_bookings": provider.total_bookings,
            "availability_status": provider.availability_status,
            "background_verified": provider.background_verified,
        },
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.strftime("%Y-%m-%d")
            }
            for r in reviews
        ]
    }


@router.get("/service/{service_type}", response_model=List[ProviderOut])
def get_providers_by_service(service_type: str, db: Session = Depends(get_db)):
    return db.query(Provider).filter(
        Provider.service_type == service_type,
        Provider.availability_status == "available"
    ).all()


@router.patch("/{provider_id}/verify")
def verify_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider.background_verified = "verified"
    db.commit()
    return {"message": "Provider verified successfully"}

