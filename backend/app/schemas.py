# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import date, time, datetime
from typing import Optional
from pydantic import ConfigDict


# User Schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Provider Schemas
class ProviderCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str       # <--- MUST be present and valid string
    password: str
    service_type: str
    experience_years: int = 0
    hourly_rate: float
    location: Optional[str] = None # <--- Optional, but required if sent
    bio: Optional[str] = None

class ProviderOut(BaseModel):
    id: int
    user_id: int
    service_type: str
    experience_years: int
    hourly_rate: float
    location: Optional[str]
    rating: float
    total_bookings: int
    availability_status: str
    background_verified: str
    user: UserOut

    model_config = ConfigDict(from_attributes=True)


# Service Schemas
class ServiceOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    base_price: float
    category: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Booking Schemas
class BookingCreate(BaseModel):
    provider_id: int
    service_name: str
    booking_date: date
    booking_time: time
    duration_hours: int = 1
    notes: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    customer_id: int
    provider_id: int
    service_name: str
    booking_date: date
    booking_time: time
    duration_hours: int
    total_amount: float
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Review Schemas
class ReviewCreate(BaseModel):
    booking_id: int
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    booking_id: int
    provider_id: int
    customer_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)