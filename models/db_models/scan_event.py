"""Scan Event model."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class ScanEvent(Base):
    __tablename__ = "scan_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    session_id = Column(UUID(as_uuid=True), ForeignKey("production_sessions.id"), nullable=False)
    qr_code_id = Column(String, ForeignKey("qr_codes.id"), nullable=False)
    scanned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    department = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)

    notes = Column(String, nullable=True)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ProductionSession", back_populates="scans")
    qr_code = relationship("QRCode", back_populates="scans")
    user = relationship("User", back_populates="scan_events")
    dept = relationship("Department", back_populates="scans")

    def __repr__(self):
        return f"<ScanEvent(id={self.id}, scanned_at={self.scanned_at})>"
