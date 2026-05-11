"""Remarks Audit Log model."""
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from uuid import uuid4
from .base import Base

class RemarksAuditLog(Base):
    __tablename__ = "remarks_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    remark_id = Column(UUID(as_uuid=True), ForeignKey("remarks.id", ondelete="CASCADE"), nullable=False)
    snapshot = Column(JSONB, nullable=False)   # Full copy of the remark row at time of edit
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
