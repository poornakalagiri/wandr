from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from db.database import get_db
from models.orm import User, Review
from models.schemas import ReviewCreate, ReviewOut
from services.auth import get_current_user, get_optional_user
import uuid

router = APIRouter()

@router.get("/")
def get_reviews(
    destination_id: Optional[str] = Query(None),
    attraction_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Review)
    if destination_id:
        q = q.filter(Review.destination_id == destination_id)
    if attraction_id:
        q = q.filter(Review.attraction_id == attraction_id)
    reviews = q.order_by(Review.created_at.desc()).limit(50).all()
    result = []
    for r in reviews:
        out = ReviewOut.from_orm(r)
        user = db.query(User).filter(User.id == r.user_id).first()
        if user:
            out.username = user.username
        result.append(out)
    return result

@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = Review(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **payload.model_dump()
    )
    db.add(review); db.commit(); db.refresh(review)
    out = ReviewOut.from_orm(review)
    out.username = current_user.username
    return out

@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review); db.commit()
