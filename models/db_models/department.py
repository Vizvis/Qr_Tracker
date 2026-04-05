"""Department model."""
from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .base import Base
from .enums import DepartmentStatus


class Department(Base):
    __tablename__ = "department"

    department_status_enum = SQLEnum(
        DepartmentStatus,
        name="departmentstatus",
        values_callable=lambda enum_cls: [item.value for item in enum_cls],
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    sequence_order = Column(Integer, nullable=False, unique=True)
    status = Column(department_status_enum, nullable=False, default=DepartmentStatus.ACTIVE)
    head_of_department = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_on = Column(DateTime, default=datetime.utcnow)

    # Relationships
    head = relationship("User")
    remarks = relationship("Remarks", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name={self.name}, sequence_order={self.sequence_order})>"
