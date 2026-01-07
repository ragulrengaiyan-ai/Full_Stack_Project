from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Items (Legacy/Test) ---
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True

# --- Users ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Providers ---
class ProviderBase(BaseModel):
    service_type: Optional[str] = None
    experience_years: Optional[int] = 0
    hourly_rate: Optional[float] = 0.0
    location: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None

class ProviderCreate(UserCreate, ProviderBase):
    pass

class ProviderOut(ProviderBase):
    id: int
    user_id: int
    background_verified: str
    availability_status: str
    rating: float
    total_bookings: int
    earnings: float
    user: Optional[UserOut] = None
    class Config:
        from_attributes = True

# --- Bookings ---
class BookingBase(BaseModel):
    provider_id: int
    service_name: str
    booking_date: str
    booking_time: str
    duration_hours: int
    address: str
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int
    customer_id: int
    total_amount: float
    commission_amount: float
    provider_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# --- Reviews ---
class ReviewCreate(BaseModel):
    booking_id: int
    rating: int
    comment: Optional[str] = None

class ReviewOut(ReviewCreate):
    id: int
    provider_id: int
    customer_id: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Complaints ---
class ComplaintCreate(BaseModel):
    booking_id: int
    subject: str
    description: str

class ComplaintOut(ComplaintCreate):
    id: int
    customer_id: int
    status: str
    resolution: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True