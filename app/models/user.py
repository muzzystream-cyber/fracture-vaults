from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    xp = Column(Integer, default=0)
    observer_rank = Column(String, default="Novice Observer")
    referral_code = Column(String, unique=True, nullable=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    watchlists = relationship("Watchlist", back_populates="user")
    paper_account = relationship("PaperAccount", back_populates="user", uselist=False)
    xp_events = relationship("XPEvent", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")

class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    experience_level = Column(String, default="beginner")
    learning_tone = Column(String, default="professional")
    tooltips_enabled = Column(Boolean, default=True)
    tutorials_enabled = Column(Boolean, default=True)
    ambient_music_enabled = Column(Boolean, default=True)
    user = relationship("User", back_populates="preferences")

class XPEvent(Base, TimestampMixin):
    __tablename__ = "xp_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String, nullable=False)
    xp_awarded = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    user = relationship("User", back_populates="xp_events")

class UserBadge(Base, TimestampMixin):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_key = Column(String, nullable=False)
    badge_name = Column(String, nullable=False)
    user = relationship("User", back_populates="badges")
