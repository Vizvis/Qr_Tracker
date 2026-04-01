"""Remarks model."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4
from .base import Base


class Remarks(Base):
    __tablename__ = "remarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    qr_id = Column(UUID(as_uuid=True), ForeignKey("qr_codes.id"), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=True)
    general_remarks = Column(String, nullable=True)
    issue_remarks = Column(String, nullable=True)

    qr_code = relationship("QRCode", back_populates="remarks")
    department = relationship("Department", back_populates="remarks")

    def __repr__(self):
        return f"<Remarks(id={self.id})>"
