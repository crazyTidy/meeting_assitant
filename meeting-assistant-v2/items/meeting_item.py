#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Pydantic schemas for meetings."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.meeting_model import MeetingStatus, ProcessingStage


# Participant Schemas
class ParticipantItem(BaseModel):
    """Base participant schema."""
    speaker_id: str
    display_name: str


class ParticipantCreateItem(ParticipantItem):
    """Schema for creating a participant."""
    voice_segment_path: Optional[str] = None


class ParticipantUpdateItem(BaseModel):
    """Schema for updating a participant."""
    display_name: str = Field(..., min_length=1, max_length=100)


class ParticipantResponseItem(ParticipantItem):
    """Schema for participant response."""
    id: str
    voice_segment_path: Optional[str] = None

    class Config:
        from_attributes = True


# Speaker Segment Schemas
class SpeakerSegmentResponseItem(BaseModel):
    """Schema for speaker segment response."""
    id: str
    participant_id: Optional[str] = None
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    transcript: Optional[str] = None
    segment_index: Optional[int] = None

    class Config:
        from_attributes = True


# Merged Segment Schemas
class MergedSegmentResponseItem(BaseModel):
    """Schema for merged segment response."""
    id: str
    participant_id: Optional[str] = None
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    transcript: Optional[str] = None
    segment_count: int
    segment_index: int

    class Config:
        from_attributes = True


# Summary Schemas
class SummaryItem(BaseModel):
    """Base summary schema."""
    content: str


class SummaryResponseItem(SummaryItem):
    """Schema for summary response."""
    id: str
    generated_at: datetime

    class Config:
        from_attributes = True


# Meeting Schemas
class MeetingCreateItem(BaseModel):
    """Schema for creating a meeting (used internally)."""
    title: str = Field(..., min_length=1, max_length=255)
    audio_path: str


class MeetingResponseItem(BaseModel):
    """Schema for meeting response."""
    id: str
    title: str
    status: MeetingStatus
    progress: int
    stage: Optional[ProcessingStage] = None
    duration: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingDetailResponseItem(MeetingResponseItem):
    """Schema for detailed meeting response."""
    participants: List[ParticipantResponseItem] = []
    speaker_segments: List[SpeakerSegmentResponseItem] = []
    merged_segments: List[MergedSegmentResponseItem] = []
    summary: Optional[SummaryResponseItem] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class MeetingStatusResponseItem(BaseModel):
    """Schema for meeting status response."""
    id: str
    status: MeetingStatus
    progress: int
    stage: Optional[ProcessingStage] = None
    message: str
    stage_description: Optional[str] = None  # 人类可读的阶段描述


class MeetingListResponseItem(BaseModel):
    """Schema for paginated meeting list."""
    items: List[MeetingResponseItem]
    total: int
    page: int
    size: int
    pages: int


# Error Schema
class ErrorResponseItem(BaseModel):
    """Schema for error response."""
    error: dict = Field(
        ...,
        example={"code": "VALIDATION_ERROR", "message": "Invalid input"}
    )
