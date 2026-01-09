import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid6 import uuid7

from ..core.db.database import Base


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_by_user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    title = Column(String(30), nullable=False)
    text = Column(String(63206), nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid7, unique=True, nullable=False)
    media_url = Column(String, nullable=True, default=None)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
    is_deleted = Column(Boolean, default=False, index=True, nullable=False)
