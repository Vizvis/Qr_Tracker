"""Remarks model."""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base


class Remarks(Base):
    __tablename__ = "remarks"
    __table_args__ = (
        UniqueConstraint(
            "qr_id",
            "item_id",
            "department_id",
            name="uq_remarks_qr_item_department",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    qr_id = Column(String, ForeignKey("qr_codes.id"), nullable=True)
    item_id = Column(String, nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=True)
    general_remarks = Column(String, nullable=True)
    issue_remarks = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    qr_code = relationship("QRCode", back_populates="remarks")
    department = relationship("Department", back_populates="remarks")

    def __repr__(self):
        return f"<Remarks(id={self.id})>"
