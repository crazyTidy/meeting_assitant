#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Speaker Segment database model."""
import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from .database import Base


class SpeakerSegment(Base):
    """Speaker segment model for storing timeline of speech segments."""

    __tablename__ = "speaker_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(
        String(36),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    participant_id = Column(
        String(36),
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=True
    )
    speaker_id = Column(String(50), nullable=False, index=True)  # e.g., "speaker_1"

    # Time information
    start_time = Column(Float, nullable=False)  # Start time in seconds
    end_time = Column(Float, nullable=False)    # End time in seconds
    duration = Column(Float, nullable=False)     # Duration in seconds

    # Content
    transcript = Column(Text, nullable=True)     # Transcribed text for this segment

    # Additional metadata
    segment_index = Column(Integer, nullable=True)  # Order in the timeline

    # Relationship
    meeting = relationship("Meeting", back_populates="speaker_segments")
    participant = relationship("Participant")

    def __repr__(self):
        return f"<SpeakerSegment(id={self.id}, speaker={self.speaker_id}, start={self.start_time}, end={self.end_time})>"
