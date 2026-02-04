from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
try:
    from ..database import get_db
    from ..models import Complaint, Booking, User
    from ..schemas import ComplaintCreate, ComplaintOut
except (ImportError, ValueError):
    from database import get_db
    from models import Complaint, Booking, User
    from schemas import ComplaintCreate, ComplaintOut

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint: ComplaintCreate, customer_id: int, db: Session = Depends(get_db)):
    # Check if booking exists and belongs to customer
    booking = db.query(Booking).filter(Booking.id == complaint.booking_id, Booking.customer_id == customer_id).first()
    if not booking:
        raise HTTPException(
            status_code=404, 
            detail=f"Booking #{complaint.booking_id} not found or not owned by customer #{customer_id}"
        )
    
    try:
        new_complaint = Complaint(
            booking_id=complaint.booking_id,
            customer_id=customer_id,
            subject=complaint.subject,
            description=complaint.description,
            status="pending" # Explicitly set status to prevent null serialization issues
        )
        db.add(new_complaint)
        db.commit()
        db.refresh(new_complaint)
        return new_complaint
    except Exception as e:
        db.rollback()
        # Extract the original database error if available
        error_msg = str(e)
        if hasattr(e, 'orig') and e.orig:
            error_msg = str(e.orig)
        
        print(f"CRITICAL COMPLAINT ERROR: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Database Error: {error_msg}"
        )

@router.get("/", response_model=List[ComplaintOut])
def get_all_complaints(db: Session = Depends(get_db)):
    try:
        # Simple list for admin. In real app, check admin role.
        return db.query(Complaint).all()
    except Exception as e:
        print(f"Error fetching complaints: {e}")
        return []

@router.get("/customer/{customer_id}", response_model=List[ComplaintOut])
def get_customer_complaints(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Complaint).filter(Complaint.customer_id == customer_id).all()

class ComplaintResolve(BaseModel):
    resolution: str

@router.patch("/{complaint_id}/resolve")
def resolve_complaint(complaint_id: int, resolve_data: ComplaintResolve, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "resolved"
    complaint.resolution = resolve_data.resolution
    db.commit()
    return {"message": "Complaint marked as resolved"}

@router.patch("/{complaint_id}/investigate")
def investigate_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "investigating"
    db.commit()
    return {"message": "Complaint status changed to investigating"}

@router.patch("/{complaint_id}/refund")
def refund_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Update complaint status
    complaint.status = "refunded"
    complaint.resolution = "System-initiated refund processed for the customer."
    
    # Update booking status
    booking = complaint.booking
    if booking:
        booking.refund_status = "processed"
        booking.status = "cancelled" 
        
    db.commit()
    return {"message": "Refund processed and complaint updated"}

@router.patch("/{complaint_id}/warn")
def warn_provider(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "warned"
    complaint.admin_notes = "Official warning issued to provider based on this complaint."
    
    db.commit()
    return {"message": "Provider warned and complaint updated"}
