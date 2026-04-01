"""User model."""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base
from .enums import RoleLevel


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleLevel), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    created_qrs = relationship("QRCode", foreign_keys="QRCode.registered_by")
    enabled_qrs = relationship("QRCode", foreign_keys="QRCode.enabled_by")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
