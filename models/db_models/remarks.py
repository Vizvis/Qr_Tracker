"""Remarks model."""
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
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
    custom_data = Column(JSONB, default=dict, server_default='{}', nullable=False)
    remarks_history = Column(JSONB, default=list, server_default='[]', nullable=False)
    remark_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    remark_updated = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    qr_code = relationship("QRCode", back_populates="remarks")
    department = relationship("Department", back_populates="remarks")
    creator = relationship("User", foreign_keys=[remark_by])
    updater = relationship("User", foreign_keys=[remark_updated])

    def __repr__(self):
        return f"<Remarks(id={self.id})>"
