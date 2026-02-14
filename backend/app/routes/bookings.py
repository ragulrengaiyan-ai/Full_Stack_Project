# app/routes/bookings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

try:
    from ..database import get_db
    from ..models import Booking, Provider
    from ..schemas import BookingCreate, BookingOut, BookingUpdate
except (ImportError, ValueError):
    from database import get_db
    from models import Booking, Provider
    from schemas import BookingCreate, BookingOut, BookingUpdate

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(booking: BookingCreate, customer_id: int, db: Session = Depends(get_db)):
    try:
        # Get provider to calculate total amount
        provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        # Check for overlaps
        existing_booking = db.query(Booking).filter(
            Booking.provider_id == booking.provider_id,
            Booking.booking_date == booking.booking_date,
            Booking.status.in_(["pending", "confirmed"])
        ).first()
        
        if existing_booking:
            raise HTTPException(
                status_code=400, 
                detail=f"Professional is already booked on this date. Please choose another date or professional."
            )

        # Ensure hourly_rate is not None
        hourly_rate = provider.hourly_rate if provider.hourly_rate is not None else 0.0
        total_amount = hourly_rate * booking.duration_hours
        
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
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"CRITICAL BOOKING ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")


@router.get("/customer/{customer_id}", response_model=List[BookingOut])
def get_customer_bookings(customer_id: int, db: Session = Depends(get_db)):
    try:
        from sqlalchemy.orm import joinedload
        bookings = db.query(Booking).options(
            joinedload(Booking.customer),
            joinedload(Booking.provider).joinedload(Provider.user)
        ).filter(Booking.customer_id == customer_id).all()
        return bookings
    except Exception as e:
        print(f"Error fetching customer bookings: {e}")
        return []


@router.get("/provider/{provider_id}", response_model=List[BookingOut])
def get_provider_bookings(provider_id: int, db: Session = Depends(get_db)):
    from sqlalchemy.orm import joinedload
    bookings = db.query(Booking).options(
        joinedload(Booking.customer),
        joinedload(Booking.provider).joinedload(Provider.user)
    ).filter(Booking.provider_id == provider_id).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/status")
def update_booking_status(booking_id: int, new_status: str, db: Session = Depends(get_db)):
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # If moving to completed, calculate split
        if new_status == "completed" and booking.status != "completed":
            commission_rate = 0.15
            total_amount = booking.total_amount if booking.total_amount is not None else 0.0
            booking.commission_amount = total_amount * commission_rate
            booking.provider_amount = total_amount - booking.commission_amount
            
            # Update provider's total earnings
            provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
            if provider:
                provider.earnings += booking.provider_amount
                
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"Booking status updated to {new_status}"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"CRITICAL STATUS UPDATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update booking status: {str(e)}")


@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Booking cancelled successfully"}


@router.patch("/{booking_id}", response_model=BookingOut)
def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.status not in ["pending", "confirmed"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot edit booking in '{booking.status}' status."
            )

        update_data = booking_update.dict(exclude_unset=True)
        
        # Check for overlaps if date is changed
        if "booking_date" in update_data and update_data["booking_date"] != booking.booking_date:
            existing_booking = db.query(Booking).filter(
                Booking.provider_id == booking.provider_id,
                Booking.booking_date == update_data["booking_date"],
                Booking.status.in_(["pending", "confirmed"]),
                Booking.id != booking_id
            ).first()
            
            if existing_booking:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Professional is already booked on this date. Please choose another date."
                )

        # Recalculate total amount if duration is changed
        if "duration_hours" in update_data:
            provider = db.query(Provider).filter(Provider.id == booking.provider_id).first()
            if provider:
                hourly_rate = provider.hourly_rate if provider.hourly_rate is not None else 0.0
                booking.total_amount = hourly_rate * update_data["duration_hours"]

        for key, value in update_data.items():
            setattr(booking, key, value)
            
        booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(booking)
        
        return booking
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"CRITICAL BOOKING UPDATE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")


@router.patch("/{booking_id}/reschedule")
def request_reschedule(booking_id: int, suggested_date: str, suggested_time: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.suggested_date = suggested_date
    booking.suggested_time = suggested_time
    booking.status = "reschedule_requested"
    booking.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Reschedule request sent to customer"}


@router.patch("/{booking_id}/reschedule/response")
def handle_reschedule_response(booking_id: int, accept: bool, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if accept:
        booking.booking_date = booking.suggested_date
        booking.booking_time = booking.suggested_time
        booking.status = "confirmed"
    else:
        booking.status = "pending"

    booking.suggested_date = None
    booking.suggested_time = None
    booking.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Reschedule response processed"}
