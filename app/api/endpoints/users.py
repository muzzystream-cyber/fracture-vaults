from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

@router.get("/me")
def get_me(current_user=Depends(get_current_active_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "xp": current_user.xp,
        "observer_rank": current_user.observer_rank,
        "referral_code": current_user.referral_code,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin
    }

class PreferenceUpdate(BaseModel):
    experience_level: str = "beginner"
    learning_tone: str = "professional"
    tooltips_enabled: bool = True
    tutorials_enabled: bool = True
    ambient_music_enabled: bool = True

@router.get("/me/preferences")
def get_preferences(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.user import UserPreference
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.put("/me/preferences")
def update_preferences(pref_in: PreferenceUpdate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.user import UserPreference
    prefs = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not prefs:
        prefs = UserPreference(user_id=current_user.id)
        db.add(prefs)
    for field, value in pref_in.dict().items():
        setattr(prefs, field, value)
    db.commit()
    db.refresh(prefs)
    return prefs
