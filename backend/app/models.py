from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
try:
    from .database import Base
except (ImportError, ValueError):
    from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    password = Column(String)
    role = Column(String) # customer, provider, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    provider_profile = relationship("Provider", back_populates="user", uselist=False, cascade="all, delete-orphan")
    bookings_as_customer = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")

class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String)
    experience_years = Column(Integer)
    hourly_rate = Column(Float)
    location = Column(String)
    address = Column(String, nullable=True) # Address is now linked/required during registration
    bio = Column(Text)
    background_verified = Column(String, default="pending") # pending, verified, rejected
    availability_status = Column(String, default="available") # available, busy, offline
    rating = Column(Float, default=0.0)
    total_bookings = Column(Integer, default=0)
    earnings = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="provider_profile")
    bookings = relationship("Booking", back_populates="provider", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="provider", cascade="all, delete-orphan")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    provider_id = Column(Integer, ForeignKey("providers.id"))
    service_name = Column(String)
    booking_date = Column(String) 
    booking_time = Column(String)
    duration_hours = Column(Integer)
    total_amount = Column(Float)
    commission_amount = Column(Float, default=0.0)
    provider_amount = Column(Float, default=0.0)
    address = Column(Text)
    notes = Column(Text)
    status = Column(String, default="pending") # pending, accepted, completed, cancelled, reschedule_requested
    suggested_date = Column(String, nullable=True)
    suggested_time = Column(String, nullable=True)
    refund_status = Column(String, nullable=True) # None, processed, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="bookings_as_customer")
    provider = relationship("Provider", back_populates="bookings")
    complaints = relationship("Complaint", back_populates="booking", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    provider_id = Column(Integer, ForeignKey("providers.id"))
    customer_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    provider = relationship("Provider", back_populates="reviews")
    booking = relationship("Booking", back_populates="review")

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    customer_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    description = Column(Text)
    status = Column(String, default="pending") # pending, investigating, resolved, refunded, warned
    resolution = Column(Text)
    admin_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="complaints")

class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String, nullable=True)
    subject = Column(String)
    message = Column(Text)
    status = Column(String, default="new") # new, read, replied
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    base_price = Column(Float)
    image_url = Column(String, nullable=True)

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)