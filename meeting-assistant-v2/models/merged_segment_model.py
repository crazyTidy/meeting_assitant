#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Merged speaker segment database model."""
import uuid
from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class MergedSegment(Base):
    """Merged speaker segment model - combines consecutive segments from the same speaker."""

    __tablename__ = "merged_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(
        String(36),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="SET NULL"), nullable=True)
    speaker_id = Column(String(50), nullable=False)  # e.g., "speaker_1"
    start_time = Column(Float, nullable=False)  # Start time in seconds
    end_time = Column(Float, nullable=False)  # End time in seconds
    duration = Column(Float, nullable=False)  # Duration in seconds
    transcript = Column(Text, nullable=True)  # Combined transcript text
    segment_count = Column(Integer, nullable=False, default=1)  # Number of original segments merged
    segment_index = Column(Integer, nullable=False)  # Order in merged timeline

    # Relationship
    meeting = relationship("Meeting", back_populates="merged_segments")
    participant = relationship("Participant", foreign_keys=[participant_id])

    def __repr__(self):
        return f"<MergedSegment(id={self.id}, speaker={self.speaker_id}, start={self.start_time}, end={self.end_time}, count={self.segment_count})>"
