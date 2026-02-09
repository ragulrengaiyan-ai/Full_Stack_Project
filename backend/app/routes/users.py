# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

try:
    from ..database import get_db
    from ..schemas import UserCreate, UserOut, UserLogin, ProviderCreate, ProviderOut
    from ..models import User, Provider, Booking, Review, Complaint
    from ..auth import generate_password_hash, verify_password, create_access_token, get_current_user
except (ImportError, ValueError):
    from database import get_db
    from schemas import UserCreate, UserOut, UserLogin, ProviderCreate, ProviderOut
    from models import User, Provider, Booking, Review, Complaint
    from auth import generate_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

@router.post("/register/customer", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_customer(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = generate_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        password=hashed_password,
        role="customer"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/register/provider", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
def register_provider(provider_data: ProviderCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == provider_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user account
    hashed_password = generate_password_hash(provider_data.password)
    new_user = User(
        name=provider_data.name,
        email=provider_data.email,
        phone=provider_data.phone,
        password=hashed_password,
        role="provider"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create provider profile
    new_provider = Provider(
        user_id=new_user.id,
        service_type=provider_data.service_type,
        experience_years=provider_data.experience_years,
        hourly_rate=provider_data.hourly_rate,
        location=provider_data.location,
        address=provider_data.address,
        bio=provider_data.bio
    )
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    
    return new_provider


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    access_token = create_access_token(data={"sub": user.email})

    return {
        "message": "Login successful",
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username', not 'email'
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    access_token = create_access_token(data={"sub": user.email})

    # OAuth2 spec requires exactly this JSON structure
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/{user_id}", response_model=UserOut)
def get_current_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name:
        user.name = user_update.name
    if user_update.email:
        # Check if email is taken by another user
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing and existing.id != user_id:
             raise HTTPException(status_code=400, detail="Email already in use")
        user.email = user_update.email
    if user_update.phone:
        user.phone = user_update.phone
        
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_account(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.id != user_id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to delete this account")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Cascade Delete Logic
        # 1. Handle Provider Profile and dependency chain
        provider = db.query(Provider).filter(Provider.user_id == user_id).first()
        if provider:
            # Delete everything linked to provider's bookings
            p_booking_ids = [b.id for b in db.query(Booking.id).filter(Booking.provider_id == provider.id).all()]
            if p_booking_ids:
                db.query(Review).filter(Review.booking_id.in_(p_booking_ids)).delete(synchronize_session=False)
                db.query(Complaint).filter(Complaint.booking_id.in_(p_booking_ids)).delete(synchronize_session=False)
                db.query(Booking).filter(Booking.id.in_(p_booking_ids)).delete(synchronize_session=False)
            
            # Delete provider reviews directly
            db.query(Review).filter(Review.provider_id == provider.id).delete(synchronize_session=False)
            db.delete(provider)
        
        # 2. Handle Customer activity
        db.query(Review).filter(Review.customer_id == user_id).delete(synchronize_session=False)
        db.query(Complaint).filter(Complaint.customer_id == user_id).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.customer_id == user_id).delete(synchronize_session=False)
        
        # 3. Final User Deletion
        db.delete(user)
        db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database deletion failed: {str(e)}")