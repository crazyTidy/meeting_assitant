"""Summary database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Summary(Base):
    """Meeting summary model."""

    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(
        String(36),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    content = Column(Text, nullable=False)  # Markdown content
    raw_response = Column(Text, nullable=True)  # Raw LLM response
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    meeting = relationship("Meeting", back_populates="summary")

    def __repr__(self):
        return f"<Summary(id={self.id}, meeting_id={self.meeting_id})>"
