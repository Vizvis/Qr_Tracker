"""QR Code model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(String, primary_key=True)  # Provided by client (scanned from physical tag)
    status = Column(Enum("pending", "active", "inactive", name="qr_status"), default="pending", nullable=False)
    registered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    enabled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    enabled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[registered_by])
    enabler = relationship("User", foreign_keys=[enabled_by])
    produced_items = relationship("ProducedItems", back_populates="qr_code")
    remarks = relationship("Remarks", back_populates="qr_code")

    def __repr__(self):
        return f"<QRCode(id={self.id}, status={self.status})>"
