# app/routes/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

try:
    from ..database import get_db
    from ..models import Review, Booking, Provider, User
    from ..schemas import ReviewCreate, ReviewOut
except (ImportError, ValueError):
    from database import get_db
    from models import Review, Booking, Provider, User
    from schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
def create_review(review: ReviewCreate, customer_id: int, db: Session = Depends(get_db)):
    # Check if booking exists
    booking = db.query(Booking).filter(Booking.id == review.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if booking belongs to customer
    if booking.customer_id != customer_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Only completed services can be reviewed
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="Only completed bookings can be reviewed")
    
    # Check if review already exists
    existing_review = db.query(Review).filter(Review.booking_id == review.booking_id).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Review already exists for this booking")
    
    # Create review
    new_review = Review(
        booking_id=review.booking_id,
        provider_id=booking.provider_id,
        customer_id=customer_id,
        rating=review.rating,
        comment=review.comment
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    # Update provider rating
    provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
    reviews = db.query(Review).filter(Review.provider_id == provider.id).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        provider.rating = round(avg_rating, 1)
        db.commit()
    
    return new_review


@router.get("/provider/{provider_id}", response_model=List[ReviewOut])
def get_provider_reviews(provider_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.provider_id == provider_id).all()
    return reviews

@router.get("/customer/{customer_id}", response_model=List[ReviewOut])
def get_customer_reviews(customer_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.customer_id == customer_id).all()
    # Ideally we'd join with Provider/User to get names, but schema ReviewOut uses IDs.
    # Frontend can fetch names or we update schema. For simple mode, IDs might suffice or we enrich return.
    return reviews