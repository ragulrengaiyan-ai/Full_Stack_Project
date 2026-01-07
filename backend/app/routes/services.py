from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Service

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/")
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()
