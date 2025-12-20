from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Complaint, Booking, User
from app.schemas import ComplaintCreate, ComplaintOut

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("/", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint: ComplaintCreate, customer_id: int, db: Session = Depends(get_db)):
    # Check if booking exists and belongs to customer
    booking = db.query(Booking).filter(Booking.id == complaint.booking_id, Booking.customer_id == customer_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not owned by you")
    
    new_complaint = Complaint(
        booking_id=complaint.booking_id,
        customer_id=customer_id,
        subject=complaint.subject,
        description=complaint.description
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    return new_complaint

@router.get("/", response_model=List[ComplaintOut])
def get_all_complaints(db: Session = Depends(get_db)):
    # Simple list for admin. In real app, check admin role.
    return db.query(Complaint).all()

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
