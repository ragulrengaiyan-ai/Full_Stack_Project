from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
try:
    from ..database import get_db
    from ..models import Inquiry
    from ..schemas import InquiryCreate, InquiryOut
except (ImportError, ValueError):
    from database import get_db
    from models import Inquiry
    from schemas import InquiryCreate, InquiryOut

router = APIRouter(prefix="/inquiries", tags=["Inquiries"])

@router.post("/", response_model=InquiryOut, status_code=status.HTTP_201_CREATED)
def create_inquiry(inquiry: InquiryCreate, db: Session = Depends(get_db)):
    new_inquiry = Inquiry(**inquiry.dict())
    db.add(new_inquiry)
    db.commit()
    db.refresh(new_inquiry)
    return new_inquiry

@router.get("/", response_model=List[InquiryOut])
def get_all_inquiries(db: Session = Depends(get_db)):
    try:
        # In real app, check admin role
        return db.query(Inquiry).all()
    except Exception as e:
        print(f"Error fetching inquiries: {e}")
        return []

@router.patch("/{inquiry_id}/status")
def update_inquiry_status(inquiry_id: int, status: str, db: Session = Depends(get_db)):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    inquiry.status = status
    db.commit()
    return {"message": "Inquiry status updated"}
