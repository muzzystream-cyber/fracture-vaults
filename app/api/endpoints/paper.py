from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from app.db.session import get_db
from app.api.deps import get_current_active_user

router = APIRouter()

class TradeIn(BaseModel):
    symbol: str
    side: str
    quantity: float
    price: float

def award_xp(db, user, event_type: str, xp: int, description: str):
    from app.models.user import XPEvent
    from app.api.endpoints.auth import get_rank
    event = XPEvent(user_id=user.id, event_type=event_type, xp_awarded=xp, description=description)
    db.add(event)
    user.xp = (user.xp or 0) + xp
    user.observer_rank = get_rank(user.xp)
    db.commit()

@router.get("/account")
def get_account(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        account = PaperAccount(user_id=current_user.id, balance=Decimal("100000.0"))
        db.add(account)
        db.commit()
        db.refresh(account)
    return {"id": account.id, "balance": float(account.balance), "currency": account.currency}

@router.get("/positions")
def get_positions(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount, PaperPosition
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        return []
    positions = db.query(PaperPosition).filter(PaperPosition.account_id == account.id, PaperPosition.quantity > 0).all()
    return [{"symbol": p.symbol, "quantity": float(p.quantity), "average_price": float(p.average_price)} for p in positions]

@router.get("/trades")
def get_trades(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount, PaperTrade
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        return []
    trades = db.query(PaperTrade).filter(PaperTrade.account_id == account.id).order_by(PaperTrade.id.desc()).limit(50).all()
    return [{"id": t.id, "symbol": t.symbol, "side": t.side, "quantity": float(t.quantity), "price": float(t.price), "pnl": float(t.pnl) if t.pnl else None} for t in trades]

@router.post("/trade")
def execute_trade(trade_in: TradeIn, current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount, PaperPosition, PaperTrade
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        account = PaperAccount(user_id=current_user.id, balance=Decimal("100000.0"))
        db.add(account)
        db.commit()
        db.refresh(account)

    qty = Decimal(str(trade_in.quantity))
    price = Decimal(str(trade_in.price))
    cost = qty * price
    pnl = None

    if trade_in.side == "buy":
        if Decimal(str(account.balance)) < cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        account.balance = Decimal(str(account.balance)) - cost
        pos = db.query(PaperPosition).filter(PaperPosition.account_id == account.id, PaperPosition.symbol == trade_in.symbol).first()
        if not pos:
            pos = PaperPosition(account_id=account.id, symbol=trade_in.symbol, quantity=qty, average_price=price)
            db.add(pos)
        else:
            old_qty = Decimal(str(pos.quantity))
            old_avg = Decimal(str(pos.average_price))
            new_qty = old_qty + qty
            pos.average_price = (old_qty * old_avg + cost) / new_qty
            pos.quantity = new_qty
    elif trade_in.side == "sell":
        pos = db.query(PaperPosition).filter(PaperPosition.account_id == account.id, PaperPosition.symbol == trade_in.symbol).first()
        if not pos or Decimal(str(pos.quantity)) < qty:
            raise HTTPException(status_code=400, detail="Insufficient position")
        pnl = (price - Decimal(str(pos.average_price))) * qty
        account.balance = Decimal(str(account.balance)) + cost
        pos.quantity = Decimal(str(pos.quantity)) - qty
        if pos.quantity <= 0:
            db.delete(pos)
    else:
        raise HTTPException(status_code=400, detail="Side must be buy or sell")

    trade = PaperTrade(account_id=account.id, symbol=trade_in.symbol, side=trade_in.side, quantity=qty, price=price, pnl=pnl)
    db.add(trade)
    db.commit()
    db.refresh(trade)

    award_xp(db, current_user, "trade_executed", 5, f"Executed {trade_in.side} on {trade_in.symbol}")
    if pnl and pnl > 0:
        award_xp(db, current_user, "profitable_trade", 15, f"Profitable trade on {trade_in.symbol}")

    return {"status": "success", "trade_id": trade.id, "pnl": float(pnl) if pnl else None}

@router.get("/xp")
def get_xp(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.user import XPEvent
    events = db.query(XPEvent).filter(XPEvent.user_id == current_user.id).order_by(XPEvent.id.desc()).limit(20).all()
    return {
        "total_xp": current_user.xp,
        "observer_rank": current_user.observer_rank,
        "referral_code": current_user.referral_code,
        "recent_events": [{"type": e.event_type, "xp": e.xp_awarded, "description": e.description} for e in events]
    }
