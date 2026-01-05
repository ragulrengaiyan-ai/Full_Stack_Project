
# app/models.py
from sqlalchemy import (
    Column, Integer, String, Float,
    Date, Time, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(String(20), default="customer")
    wallet_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings_as_customer = relationship(
        "Booking",
        foreign_keys="Booking.customer_id",
        back_populates="customer"
    )

    provider_profile = relationship(
        "Provider",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    service_type = Column(String(50), nullable=False)
    experience_years = Column(Integer, default=0)
    hourly_rate = Column(Float, nullable=False)
    location = Column(String(100))
    address = Column(Text, nullable=False)
    bio = Column(Text)

    rating = Column(Float, default=0.0)
    total_bookings = Column(Integer, default=0)
    earnings = Column(Float, default=0.0)  # Total earnings for provider
    availability_status = Column(String(20), default="available")
    background_verified = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="provider_profile")
    
    # ✅ REMOVE THIS LINE - it's wrong!
    # services = relationship("Service", back_populates="provider")

    bookings = relationship(
        "Booking",
        foreign_keys="Booking.provider_id",
        back_populates="provider",
        cascade="all, delete-orphan"
    )

    reviews = relationship("Review", back_populates="provider", cascade="all, delete-orphan")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)

    service_name = Column(String(50), nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    duration_hours = Column(Integer, default=1)
    total_amount = Column(Float, nullable=False)

    status = Column(String(20), default="pending")
    payment_status = Column(String(20), default="unpaid")
    address = Column(Text, nullable=True)
    notes = Column(Text)
    
    # Tracking split
    commission_amount = Column(Float, default=0.0)
    provider_amount = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="bookings_as_customer"
    )

    provider = relationship(
        "Provider",
        foreign_keys=[provider_id],
        back_populates="bookings"
    )

    review = relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="booking", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    rating = Column(Float, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="review")
    provider = relationship("Provider", back_populates="reviews")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, resolved
    resolution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = relationship("Booking", back_populates="complaints")


# ✅ SIMPLIFIED Service model - no provider relationship
class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    base_price = Column(Float, nullable=False)
    category = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # credit, debit
    description = Column(String(255))
    reference_id = Column(String(100))
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")