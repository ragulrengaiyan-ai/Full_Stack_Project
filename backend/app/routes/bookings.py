# app/routes/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Booking, Provider
from ..schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, customer_id: int, db: Session = Depends(get_db)):
    # Get provider to calculate total amount
    provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Check for overlaps
    # A simple date-based check: if they have any confirmed booking on the same date, prevent overlap
    # More advanced: check time windows
    existing_booking = db.query(Booking).filter(
        Booking.provider_id == booking.provider_id,
        Booking.booking_date == booking.booking_date,
        Booking.status.in_(["pending", "confirmed"])
    ).first()
    
    if existing_booking:
        # Check if the time periods overlap
        # duration_hours is used to calculate end time
        # This is a basic check.
        raise HTTPException(
            status_code=400, 
            detail=f"Professional is already booked on this date. Please choose another date or professional."
        )

    total_amount = provider.hourly_rate * booking.duration_hours
    
    new_booking = Booking(
        customer_id=customer_id,
        provider_id=booking.provider_id,
        service_name=booking.service_name,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time,
        duration_hours=booking.duration_hours,
        total_amount=total_amount,
        address=booking.address,
        notes=booking.notes,
        status="pending"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # Update provider stats
    provider.total_bookings += 1
    db.commit()
    
    return new_booking


@router.get("/customer/{customer_id}", response_model=List[BookingOut])
def get_customer_bookings(customer_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.customer_id == customer_id).all()
    return bookings


@router.get("/provider/{provider_id}", response_model=List[BookingOut])
def get_provider_bookings(provider_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.provider_id == provider_id).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/status")
def update_booking_status(booking_id: int, new_status: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # If moving to completed, calculate split
    if new_status == "completed" and booking.status != "completed":
        commission_rate = 0.15
        booking.commission_amount = booking.total_amount * commission_rate
        booking.provider_amount = booking.total_amount - booking.commission_amount
        
        # Update provider's total earnings
        provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
        if provider:
            provider.earnings += booking.provider_amount
            
    booking.status = new_status
    booking.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"Booking status updated to {new_status}"}


@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Booking cancelled successfully"}