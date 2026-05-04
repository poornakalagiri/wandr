from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.orm import User
from models.schemas import UserCreate, UserLogin, UserOut, Token
from services.auth import hash_password, verify_password, create_access_token, get_current_user
import uuid

router = APIRouter()

@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        id=str(uuid.uuid4()),
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, token_type="bearer", user=UserOut.from_orm(user))

@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.id})
    return Token(access_token=token, token_type="bearer", user=UserOut.from_orm(user))

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserOut)
def update_profile(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allowed = {"full_name", "avatar_url"}
    for k, v in payload.items():
        if k in allowed:
            setattr(current_user, k, v)
    db.commit(); db.refresh(current_user)
    return current_user
