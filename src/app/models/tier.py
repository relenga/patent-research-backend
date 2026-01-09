from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, String

from ..core.db.database import Base


class Tier(Base):
    __tablename__ = "tier"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)
