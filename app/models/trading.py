from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, Date, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.user import TimestampMixin

class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    user = relationship("User", back_populates="watchlists")
    assets = relationship("WatchlistAsset", back_populates="watchlist", cascade="all, delete-orphan")

class WatchlistAsset(Base, TimestampMixin):
    __tablename__ = "watchlist_assets"
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"))
    symbol = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="yahoo")
    watchlist = relationship("Watchlist", back_populates="assets")

class StrategySignal(Base, TimestampMixin):
    __tablename__ = "strategy_signals"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    strategy_name = Column(String, index=True, nullable=False)
    signal_type = Column(String, nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    metadata_json = Column(JSON)
    version = Column(String, default="1.0")

class PaperAccount(Base, TimestampMixin):
    __tablename__ = "paper_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    balance = Column(Numeric(20, 8), default=100000.0)
    currency = Column(String, default="USD")
    user = relationship("User", back_populates="paper_account")
    positions = relationship("PaperPosition", back_populates="account")
    trades = relationship("PaperTrade", back_populates="account")
    snapshots = relationship("PaperDailySnapshot", back_populates="account")

class PaperPosition(Base, TimestampMixin):
    __tablename__ = "paper_positions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("paper_accounts.id"))
    symbol = Column(String, nullable=False)
    quantity = Column(Numeric(20, 8), default=0)
    average_price = Column(Numeric(20, 8), default=0)
    account = relationship("PaperAccount", back_populates="positions")

class PaperTrade(Base, TimestampMixin):
    __tablename__ = "paper_trades"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("paper_accounts.id"))
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    pnl = Column(Numeric(20, 8), nullable=True)
    signal_id = Column(Integer, ForeignKey("strategy_signals.id"), nullable=True)
    account = relationship("PaperAccount", back_populates="trades")

class PaperDailySnapshot(Base, TimestampMixin):
    __tablename__ = "paper_daily_snapshots"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("paper_accounts.id"))
    date = Column(Date, nullable=False)
    equity = Column(Numeric(20, 8), nullable=False)
    account = relationship("PaperAccount", back_populates="snapshots")
