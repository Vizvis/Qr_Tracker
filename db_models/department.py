"""Department model."""
from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base
from .enums import DepartmentEnum


class Department(Base):
    __tablename__ = "department"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dept_type = Column(SQLEnum(DepartmentEnum), nullable=False, default=DepartmentEnum.PRODUCTION)
    head_of_department = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_on = Column(DateTime, default=datetime.utcnow)

    # Relationships
    head = relationship("User")
    scans = relationship("ScanEvent", back_populates="dept")
    produced_items = relationship("ProducedItems", back_populates="final_dept")

    def __repr__(self):
        return f"<Department(id={self.id}, dept_type={self.dept_type})>"
