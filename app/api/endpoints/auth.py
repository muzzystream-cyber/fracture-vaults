from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
import secrets

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

OBSERVER_RANKS = [
    (0, "Novice Observer"),
    (100, "The Watcher"),
    (500, "Keeper of Signals"),
    (1500, "Fracture Reader"),
    (3000, "Inner Marches Guard"),
    (6000, "Elder of the Vault"),
    (10000, "The Unseen")
]

def get_rank(xp: int) -> str:
    rank = OBSERVER_RANKS[0][1]
    for threshold, name in OBSERVER_RANKS:
        if xp >= threshold:
            rank = name
    return rank

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    from app.models.user import User, UserPreference, XPEvent
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        xp=10,
        observer_rank="Novice Observer",
        referral_code=secrets.token_urlsafe(8)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    prefs = UserPreference(user_id=user.id)
    db.add(prefs)
    xp_event = XPEvent(user_id=user.id, event_type="registration", xp_awarded=10, description="Welcome to The Fracture Vaults")
    db.add(xp_event)
    db.commit()
    token = create_access_token(subject=user.id, secret_key=settings.SECRET_KEY)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from app.models.user import User
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    token = create_access_token(subject=user.id, secret_key=settings.SECRET_KEY)
    return {"access_token": token, "token_type": "bearer"}
