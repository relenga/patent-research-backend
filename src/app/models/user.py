import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from uuid6 import uuid7

from ..core.db.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(String(30), nullable=False)
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    profile_image_url = Column(String, default="https://profileimageurl.com", nullable=False)
    uuid = Column(UUID(as_uuid=True), default=uuid7, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True, default=None)
    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)
    is_deleted = Column(Boolean, default=False, index=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    tier_id = Column(Integer, ForeignKey("tier.id"), index=True, nullable=True, default=None)
