from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime
from pydantic import BaseModel
from typing import Optional
import hashlib, hmac, os, secrets
from datetime import datetime

from app.db.session import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, XPEvent, TimestampMixin
from app.db.session import Base

router = APIRouter()

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

OBSERVER_RANKS = [
    (0,     "Novice Observer"),
    (100,   "The Watcher"),
    (500,   "Keeper of Signals"),
    (1500,  "Fracture Reader"),
    (3000,  "Inner Marches Guard"),
    (6000,  "Elder of the Vault"),
    (10000, "The Unseen"),
]

XP_VALUES = {
    "social_follow_youtube":    25,
    "social_follow_tiktok":     25,
    "social_follow_instagram":  25,
    "social_follow_facebook":   25,
    "social_follow_soundcloud": 25,
    "newsletter_signup":        15,
    "newsletter_open":           5,
    "payhip_purchase":          50,
    "social_share":             20,
    "freebie_claimed":           5,
}

SOCIAL_PLATFORMS = ["youtube", "tiktok", "instagram", "facebook", "soundcloud"]

DISCOUNT_TIERS = {
    "Novice Observer":    {"pct": 0,  "code_prefix": None},
    "The Watcher":        {"pct": 5,  "code_prefix": "WATCHER5"},
    "Keeper of Signals":  {"pct": 10, "code_prefix": "KEEPER10"},
    "Fracture Reader":    {"pct": 15, "code_prefix": "FRACTURE15"},
    "Inner Marches Guard":{"pct": 20, "code_prefix": "GUARD20"},
    "Elder of the Vault": {"pct": 22, "code_prefix": "ELDER22"},
    "The Unseen":         {"pct": 25, "code_prefix": "UNSEEN25"},
}

FREEBIE_TIERS = {
    "Novice Observer":    [],
    "The Watcher":        ["clip_001", "music_001"],
    "Keeper of Signals":  ["clip_001", "clip_002", "music_001", "music_002"],
    "Fracture Reader":    ["clip_001", "clip_002", "clip_003", "music_001", "music_002", "art_001"],
    "Inner Marches Guard":["clip_001","clip_002","clip_003","clip_004","music_001","music_002","music_003","art_001","lore_001"],
    "Elder of the Vault": ["clip_001","clip_002","clip_003","clip_004","clip_005","music_001","music_002","music_003","art_001","art_002","lore_001","lore_002"],
    "The Unseen":         ["clip_001","clip_002","clip_003","clip_004","clip_005","clip_006","music_001","music_002","music_003","music_004","art_001","art_002","lore_001","lore_002","lore_003"],
}

FREEBIE_METADATA = {
    "clip_001": {"type": "clip",  "title": "The Watcher — Mines Entry",        "url": "/freebies/clips/mines_entry.mp4"},
    "clip_002": {"type": "clip",  "title": "Still Water Confirms",             "url": "/freebies/clips/still_water.mp4"},
    "clip_003": {"type": "clip",  "title": "Rune Threshold",                   "url": "/freebies/clips/rune_threshold.mp4"},
    "clip_004": {"type": "clip",  "title": "Storm Field Crossing",             "url": "/freebies/clips/storm_field.mp4"},
    "clip_005": {"type": "clip",  "title": "Gate of First Words",              "url": "/freebies/clips/gate_first_words.mp4"},
    "clip_006": {"type": "clip",  "title": "The Return — Act VI",              "url": "/freebies/clips/the_return.mp4"},
    "music_001":{"type": "music", "title": "Still Water Confirms — Suno",      "url": "/freebies/music/still_water_confirms.wav"},
    "music_002":{"type": "music", "title": "Corridor Pressure — Suno",         "url": "/freebies/music/corridor_pressure.wav"},
    "music_003":{"type": "music", "title": "Record of Entry — Suno",           "url": "/freebies/music/record_of_entry.wav"},
    "music_004":{"type": "music", "title": "Before the Crossing — Suno",       "url": "/freebies/music/before_the_crossing.wav"},
    "art_001":  {"type": "art",   "title": "BG_MINES_WATCHER — 4K PNG",        "url": "/freebies/art/mines_watcher_4k.png"},
    "art_002":  {"type": "art",   "title": "BG_STILL_WATER_MOONPOOL — 4K PNG", "url": "/freebies/art/still_water_4k.png"},
    "lore_001": {"type": "lore",  "title": "Fragment 009 — The First Crossing","url": "/freebies/lore/fragment_009.md"},
    "lore_002": {"type": "lore",  "title": "Fragment 050 — The Mines Record",  "url": "/freebies/lore/fragment_050.md"},
    "lore_003": {"type": "lore",  "title": "Fragment 100 — The Return Entry",  "url": "/freebies/lore/fragment_100.md"},
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def get_rank(xp: int) -> str:
    rank = OBSERVER_RANKS[0][1]
    for threshold, name in OBSERVER_RANKS:
        if xp >= threshold:
            rank = name
    return rank

def award_xp(db: Session, user: User, event_type: str, xp: int, description: str):
    event = XPEvent(user_id=user.id, event_type=event_type, xp_awarded=xp, description=description)
    db.add(event)
    user.xp = (user.xp or 0) + xp
    user.observer_rank = get_rank(user.xp)
    db.commit()

def already_awarded(db: Session, user_id: int, event_type: str) -> bool:
    return db.query(XPEvent).filter(XPEvent.user_id == user_id, XPEvent.event_type == event_type).first() is not None

def generate_discount_code(user_id: int, rank: str) -> Optional[str]:
    tier = DISCOUNT_TIERS.get(rank, {})
    prefix = tier.get("code_prefix")
    if not prefix:
        return None
    return f"{prefix}-{user_id}-{secrets.token_hex(4).upper()}"

class SocialFollowIn(BaseModel):
    platform: str

class NewsletterSignupIn(BaseModel):
    email: str

class ShareIn(BaseModel):
    content_id: str
    platform: str

class ClaimFreebieIn(BaseModel):
    freebie_key: str

# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.post("/social-follow")
def record_social_follow(body: SocialFollowIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    platform = body.platform.lower()
    if platform not in SOCIAL_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Unknown platform. Valid: {SOCIAL_PLATFORMS}")
    event_type = f"social_follow_{platform}"
    if already_awarded(db, current_user.id, event_type):
        return {"status": "already_recorded", "platform": platform, "xp_awarded": 0}
    xp = XP_VALUES[event_type]
    award_xp(db, current_user, event_type, xp, f"Followed FII on {platform.capitalize()}")
    all_followed = all(already_awarded(db, current_user.id, f"social_follow_{p}") for p in SOCIAL_PLATFORMS)
    bonus_xp = 0
    if all_followed and not already_awarded(db, current_user.id, "social_follow_all_platforms"):
        bonus_xp = 50
        award_xp(db, current_user, "social_follow_all_platforms", bonus_xp, "Followed FII on all 5 platforms — bonus XP awarded")
    db.refresh(current_user)
    return {"status": "recorded", "platform": platform, "xp_awarded": xp + bonus_xp, "total_xp": current_user.xp, "observer_rank": current_user.observer_rank, "all_platforms_bonus": bonus_xp > 0}


@router.post("/newsletter-signup")
def newsletter_signup(body: NewsletterSignupIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if already_awarded(db, current_user.id, "newsletter_signup"):
        return {"status": "already_recorded", "xp_awarded": 0}
    xp = XP_VALUES["newsletter_signup"]
    award_xp(db, current_user, "newsletter_signup", xp, "Subscribed to the FII newsletter")
    db.refresh(current_user)
    return {"status": "recorded", "xp_awarded": xp, "total_xp": current_user.xp, "observer_rank": current_user.observer_rank}


@router.post("/payhip-webhook")
async def payhip_webhook(request: Request, db: Session = Depends(get_db), x_payhip_signature: Optional[str] = Header(None)):
    body_bytes = await request.body()
    payhip_secret = os.getenv("PAYHIP_IPN_SECRET", "")
    if payhip_secret and x_payhip_signature:
        expected = hmac.new(payhip_secret.encode(), body_bytes, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, x_payhip_signature):
            raise HTTPException(status_code=403, detail="Invalid signature")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    buyer_email = data.get("buyer_email") or data.get("email")
    order_value = float(data.get("product_price", 0) or data.get("price", 0))
    product_name = data.get("product_title") or data.get("product_name", "FII product")
    if not buyer_email:
        return {"status": "ignored", "reason": "no buyer email"}
    user = db.query(User).filter(User.email == buyer_email).first()
    if not user:
        return {"status": "user_not_found", "email": buyer_email}
    xp = XP_VALUES["payhip_purchase"] + int(order_value)
    award_xp(db, user, "payhip_purchase", xp, f"Purchased {product_name} (£{order_value:.2f})")
    db.refresh(user)
    return {"status": "recorded", "email": buyer_email, "xp_awarded": xp, "total_xp": user.xp, "observer_rank": user.observer_rank}


@router.post("/share")
def record_share(body: ShareIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    share_key = f"social_share_{body.content_id}"
    count = db.query(XPEvent).filter(XPEvent.user_id == current_user.id, XPEvent.event_type == share_key).count()
    if count >= 3:
        return {"status": "limit_reached", "xp_awarded": 0}
    xp = XP_VALUES["social_share"]
    award_xp(db, current_user, share_key, xp, f"Shared content {body.content_id} on {body.platform}")
    db.refresh(current_user)
    return {"status": "recorded", "xp_awarded": xp, "total_xp": current_user.xp, "observer_rank": current_user.observer_rank}


@router.get("/discount")
def get_discount(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    rank = current_user.observer_rank
    tier = DISCOUNT_TIERS.get(rank, {"pct": 0, "code_prefix": None})
    code = generate_discount_code(current_user.id, rank) if tier["pct"] > 0 else None
    all_tiers = [{"rank": r, "discount_pct": DISCOUNT_TIERS[r]["pct"], "unlocked": current_user.xp >= threshold} for threshold, r in OBSERVER_RANKS]
    return {"current_rank": rank, "discount_pct": tier["pct"], "promo_code": code, "payhip_store": "https://payhip.com/ForgedInIceVaults", "instructions": f"Apply code at checkout for {tier['pct']}% off all FII products.", "all_tiers": all_tiers}


@router.get("/freebies")
def get_freebies(current_user: User = Depends(get_current_active_user)):
    rank = current_user.observer_rank
    unlocked_keys = FREEBIE_TIERS.get(rank, [])
    unlocked = [{"key": k, **FREEBIE_METADATA[k]} for k in unlocked_keys if k in FREEBIE_METADATA]
    return {"current_rank": rank, "unlocked_count": len(unlocked), "freebies": unlocked}


@router.post("/freebies/claim")
def claim_freebie(body: ClaimFreebieIn, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    rank = current_user.observer_rank
    if body.freebie_key not in FREEBIE_TIERS.get(rank, []):
        raise HTTPException(status_code=403, detail="Freebie not unlocked at your current rank")
    if body.freebie_key not in FREEBIE_METADATA:
        raise HTTPException(status_code=404, detail="Freebie not found")
    claim_event = f"freebie_claimed_{body.freebie_key}"
    if not already_awarded(db, current_user.id, claim_event):
        award_xp(db, current_user, claim_event, XP_VALUES["freebie_claimed"], f"Claimed freebie: {FREEBIE_METADATA[body.freebie_key]['title']}")
    return {"status": "claimed", "freebie": FREEBIE_METADATA[body.freebie_key]}


@router.get("/status")
def rewards_status(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    rank = current_user.observer_rank
    tier = DISCOUNT_TIERS.get(rank, {"pct": 0})
    next_rank_xp = next_rank_name = None
    for threshold, name in OBSERVER_RANKS:
        if threshold > current_user.xp:
            next_rank_xp = threshold - current_user.xp
            next_rank_name = name
            break
    platforms_followed = [p for p in SOCIAL_PLATFORMS if already_awarded(db, current_user.id, f"social_follow_{p}")]
    platforms_remaining = [p for p in SOCIAL_PLATFORMS if p not in platforms_followed]
    return {"observer_rank": rank, "total_xp": current_user.xp, "next_rank": next_rank_name, "xp_to_next_rank": next_rank_xp, "discount_pct": tier["pct"], "freebies_unlocked": len(FREEBIE_TIERS.get(rank, [])), "platforms_followed": platforms_followed, "platforms_remaining": platforms_remaining, "all_platforms_bonus_available": len(platforms_remaining) > 0}
