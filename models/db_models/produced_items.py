"""Produced Items model."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class ProducedItems(Base):
    __tablename__ = "produced_items"

    produced_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    qr_id = Column(String, ForeignKey("qr_codes.id"), nullable=False)
    item_id = Column(String, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)
    general_remarks = Column(String, nullable=True)
    issue_remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    qr_code = relationship("QRCode", back_populates="produced_items")
    department = relationship("Department", back_populates="produced_items")

    def __repr__(self):
        return f"<ProducedItems(produced_id={self.produced_id}, item_id={self.item_id})>"
