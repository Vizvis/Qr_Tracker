"""Produced Items model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base


class ProducedItems(Base):
    __tablename__ = "produced_items"

    produced_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    qr_id = Column(String, nullable=False)
    item_id = Column(String, nullable=False)
    department_name = Column(String, nullable=False)
    field_1 = Column(Integer, nullable=True, default=0)
    field_2 = Column(Integer, nullable=True, default=0)
    field_3 = Column(Integer, nullable=True, default=0)
    field_4 = Column(Integer, nullable=True, default=0)
    field_5 = Column(Integer, nullable=True, default=0)
    issue_remarks = Column(String, nullable=True)
    scanned_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    activated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    activated_at = Column(DateTime, nullable=True)
    released_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    released_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    department_sequence = Column(Integer, nullable=False, default=-1)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ProducedItems(produced_id={self.produced_id}, item_id={self.item_id})>"
