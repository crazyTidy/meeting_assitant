"""User database model for storing external user info."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User model - stores user info from external system."""

    __tablename__ = "users"

    # Primary key uses external user_id
    id = Column(String(100), primary_key=True, comment="外部系统用户ID")
    username = Column(String(100), nullable=True, comment="用户名")
    real_name = Column(String(100), nullable=True, comment="真实姓名")
    email = Column(String(100), nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    department_id = Column(String(100), nullable=True, comment="部门ID")
    department_name = Column(String(100), nullable=True, comment="部门名称")
    position = Column(String(50), nullable=True, comment="职位")
    last_seen_at = Column(DateTime, default=datetime.utcnow, comment="最后访问时间")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    created_meetings = relationship(
        "Meeting",
        back_populates="creator",
        foreign_keys="Meeting.creator_id"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, real_name={self.real_name})>"
