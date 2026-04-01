"""Production Session model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class ProductionSession(Base):
    __tablename__ = "production_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    qr_code_id = Column(String, ForeignKey("qr_codes.id"), nullable=False)

    status = Column(String, default="open")  # open, closed, voided

    batch_number = Column(String, nullable=True)
    product_type = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    session_metadata = Column(JSONB, nullable=True)

    started_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    closed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    voided_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    qr_code = relationship("QRCode", back_populates="sessions")
    scans = relationship("ScanEvent", back_populates="session")

    def __repr__(self):
        return f"<ProductionSession(id={self.id}, status={self.status})>"
