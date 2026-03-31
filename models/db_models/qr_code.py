"""QR Code model."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class QRCode(Base):
    __tablename__ = "qr_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    status = Column(String, default="pending")  # pending, active, inactive

    registered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    enabled_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    enabled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[registered_by])
    enabler = relationship("User", foreign_keys=[enabled_by])

    sessions = relationship("ProductionSession", back_populates="qr_code")
    scans = relationship("ScanEvent", back_populates="qr_code")
    produced_items = relationship("ProducedItems", back_populates="qr_code")

    def __repr__(self):
        return f"<QRCode(id={self.id}, status={self.status})>"
