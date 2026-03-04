"""Real-time transcription segment model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class RealTimeSegment(Base):
    """Real-time transcription segment."""

    __tablename__ = "real_time_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id"), nullable=False)
    speaker_id = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    meeting = relationship("Meeting", back_populates="real_time_segments")

    def __repr__(self):
        return f"<RealTimeSegment(id={self.id}, speaker={self.speaker_id}, text={self.text[:20]}...)>"
