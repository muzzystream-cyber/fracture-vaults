from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_active_user
from typing import List, Optional

router = APIRouter()

@router.get("/equity-curve")
def equity_curve(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount, PaperDailySnapshot
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        return []
    snaps = db.query(PaperDailySnapshot).filter(PaperDailySnapshot.account_id == account.id).order_by(PaperDailySnapshot.date.asc()).all()
    return [{"date": str(s.date), "equity": float(s.equity)} for s in snaps]

@router.get("/stats")
def overall_stats(current_user=Depends(get_current_active_user), db: Session = Depends(get_db)):
    from app.models.trading import PaperAccount, PaperTrade
    account = db.query(PaperAccount).filter(PaperAccount.user_id == current_user.id).first()
    if not account:
        return {"total_trades": 0, "total_pnl": 0, "win_rate": 0}
    trades = db.query(PaperTrade).filter(PaperTrade.account_id == account.id).all()
    pnls = [float(t.pnl) for t in trades if t.pnl is not None]
    wins = sum(1 for p in pnls if p > 0)
    total = len(trades)
    return {
        "total_trades": total,
        "total_pnl": round(sum(pnls), 2),
        "win_rate": round(wins / total, 4) if total > 0 else 0,
        "best_trade": max(pnls) if pnls else None,
        "worst_trade": min(pnls) if pnls else None,
        "current_balance": float(account.balance)
    }
