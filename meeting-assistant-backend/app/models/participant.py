"""Participant database model."""
import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Participant(Base):
    """Meeting participant model."""

    __tablename__ = "participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(
        String(36),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False
    )
    speaker_id = Column(String(50), nullable=False)  # e.g., "speaker_1"
    display_name = Column(String(100), nullable=False)  # User-editable name
    voice_segment_path = Column(String(512), nullable=True)

    # Relationship
    meeting = relationship("Meeting", back_populates="participants")
    speaker_segments = relationship(
        "SpeakerSegment",
        back_populates="participant",
        cascade="all, delete-orphan",
        order_by="SpeakerSegment.start_time"
    )

    def __repr__(self):
        return f"<Participant(id={self.id}, speaker_id={self.speaker_id}, name={self.display_name})>"
