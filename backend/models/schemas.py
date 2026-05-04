from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# ── Auth ──────────────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# ── Itinerary ─────────────────────────────────────────────────────────────────
class ItineraryRequest(BaseModel):
    destination_id: str
    duration_days: int
    budget_tier: str          # budget | mid | luxury
    interests: List[str] = []
    travelers: int = 1
    accessibility_needs: bool = False
    start_date: Optional[str] = None

    @field_validator("budget_tier")
    @classmethod
    def valid_tier(cls, v):
        if v not in ("budget", "mid", "luxury"):
            raise ValueError("budget_tier must be budget, mid, or luxury")
        return v

    @field_validator("duration_days")
    @classmethod
    def valid_duration(cls, v):
        if not 1 <= v <= 30:
            raise ValueError("duration_days must be between 1 and 30")
        return v

# ── Saved Trip ────────────────────────────────────────────────────────────────
class SaveTripRequest(BaseModel):
    destination_id: str
    destination_name: str
    duration_days: int
    budget_tier: str
    travelers: int = 1
    interests: List[str] = []
    itinerary_data: Dict[str, Any]
    total_cost: Optional[float] = None
    notes: Optional[str] = None

class SavedTripOut(BaseModel):
    id: str
    destination_id: str
    destination_name: str
    duration_days: int
    budget_tier: str
    travelers: int
    total_cost: Optional[float]
    notes: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

# ── Review ────────────────────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    destination_id: str
    attraction_id: Optional[str] = None
    rating: float
    title: Optional[str] = None
    body: Optional[str] = None
    visited_on: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def valid_rating(cls, v):
        if not 1.0 <= v <= 5.0:
            raise ValueError("rating must be between 1 and 5")
        return v

class ReviewOut(BaseModel):
    id: str
    destination_id: str
    attraction_id: Optional[str]
    rating: float
    title: Optional[str]
    body: Optional[str]
    visited_on: Optional[str]
    created_at: datetime
    username: Optional[str] = None
    class Config:
        from_attributes = True

# ── Search ────────────────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    budget_tier: Optional[str] = None
    continent: Optional[str] = None
    tags: Optional[List[str]] = None
