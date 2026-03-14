from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

class WatchlistCreate(BaseModel):
    name: str

class AssetAdd(BaseModel):
    symbol: str
    provider: str = "yahoo"

@router.get("/")
def list_watchlists(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import Watchlist
    wl = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()
    return [{"id": w.id, "name": w.name, "asset_count": len(w.assets)} for w in wl]

@router.post("/")
def create_watchlist(wl_in: WatchlistCreate, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import Watchlist
    from app.api.endpoints.paper import award_xp
    wl = Watchlist(user_id=current_user.id, name=wl_in.name)
    db.add(wl)
    db.commit()
    db.refresh(wl)
    award_xp(db, current_user, "watchlist_created", 10, f"Created watchlist: {wl_in.name}")
    return {"id": wl.id, "name": wl.name}

@router.post("/{watchlist_id}/assets")
def add_asset(watchlist_id: int, asset: AssetAdd, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import Watchlist, WatchlistAsset
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    wa = WatchlistAsset(watchlist_id=watchlist_id, symbol=asset.symbol.upper(), provider=asset.provider)
    db.add(wa)
    db.commit()
    return {"status": "added", "symbol": asset.symbol.upper()}

@router.delete("/{watchlist_id}/assets/{symbol}")
def remove_asset(watchlist_id: int, symbol: str, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import Watchlist, WatchlistAsset
    wl = db.query(Watchlist).filter(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    wa = db.query(WatchlistAsset).filter(WatchlistAsset.watchlist_id == watchlist_id, WatchlistAsset.symbol == symbol.upper()).first()
    if wa:
        db.delete(wa)
        db.commit()
    return {"status": "removed"}
