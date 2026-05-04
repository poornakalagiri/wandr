from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.orm import User, SavedTrip
from models.schemas import SaveTripRequest, SavedTripOut
from services.auth import get_current_user
import uuid

router = APIRouter()

@router.get("/", response_model=list[SavedTripOut])
def get_my_trips(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(SavedTrip).filter(SavedTrip.user_id == current_user.id)\
             .order_by(SavedTrip.created_at.desc()).all()

@router.post("/", response_model=SavedTripOut, status_code=201)
def save_trip(
    payload: SaveTripRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = SavedTrip(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **payload.model_dump()
    )
    db.add(trip); db.commit(); db.refresh(trip)
    return trip

@router.delete("/{trip_id}", status_code=204)
def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trip = db.query(SavedTrip).filter(
        SavedTrip.id == trip_id,
        SavedTrip.user_id == current_user.id
    ).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip); db.commit()
