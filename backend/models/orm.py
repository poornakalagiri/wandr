from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id            = Column(String, primary_key=True, default=gen_uuid)
    email         = Column(String, unique=True, index=True, nullable=False)
    username      = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name     = Column(String)
    avatar_url    = Column(String)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    saved_trips   = relationship("SavedTrip", back_populates="user", cascade="all, delete")
    reviews       = relationship("Review", back_populates="user", cascade="all, delete")

class SavedTrip(Base):
    __tablename__ = "saved_trips"
    id              = Column(String, primary_key=True, default=gen_uuid)
    user_id         = Column(String, ForeignKey("users.id"), nullable=False)
    destination_id  = Column(String, nullable=False)
    destination_name= Column(String, nullable=False)
    duration_days   = Column(Integer, nullable=False)
    budget_tier     = Column(String, nullable=False)
    travelers       = Column(Integer, default=1)
    interests       = Column(JSON, default=[])
    itinerary_data  = Column(JSON)          # full generated itinerary snapshot
    total_cost      = Column(Float)
    notes           = Column(Text)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_trips")

class Review(Base):
    __tablename__ = "reviews"
    id             = Column(String, primary_key=True, default=gen_uuid)
    user_id        = Column(String, ForeignKey("users.id"), nullable=False)
    destination_id = Column(String, nullable=False)
    attraction_id  = Column(String)
    rating         = Column(Float, nullable=False)
    title          = Column(String)
    body           = Column(Text)
    visited_on     = Column(String)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reviews")
