"""Tests for real-time transcription feature."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.meeting import Meeting, MeetingMode, MeetingStatus
from app.models.real_time_segment import RealTimeSegment
from app.repositories.realtime_segment_repository import realtime_segment_repository


@pytest.mark.asyncio
async def test_realtime_meeting_creation(client: AsyncClient, db_session):
    """Test creating a real-time meeting record."""
    meeting = Meeting(
        title="Test Real-time Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME,
        status=MeetingStatus.PROCESSING
    )
    db_session.add(meeting)
    await db_session.commit()
    await db_session.refresh(meeting)

    assert meeting.id is not None
    assert meeting.mode == MeetingMode.REAL_TIME
    assert meeting.status == MeetingStatus.PROCESSING


@pytest.mark.asyncio
async def test_realtime_segment_creation(client: AsyncClient, db_session):
    """Test creating a real-time segment."""
    # Create meeting
    meeting = Meeting(
        title="Test Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()

    # Create segment
    segment = await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="Hello world",
        start_time=0.0,
        end_time=2.5
    )

    assert segment.id is not None
    assert segment.text == "Hello world"
    assert segment.speaker_id == "SPEAKER_00"


@pytest.mark.asyncio
async def test_get_active_sessions(client: AsyncClient):
    """Test getting active transcription sessions."""
    response = await client.get("/api/v1/transcribe/active")

    assert response.status_code == 200
    data = response.json()
    assert "active_sessions" in data
    assert "count" in data
    assert isinstance(data["active_sessions"], list)


@pytest.mark.asyncio
async def test_realtime_segments_by_meeting(client: AsyncClient, db_session):
    """Test getting segments by meeting ID."""
    # Create meeting
    meeting = Meeting(
        title="Test Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()

    # Create segments
    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="First segment",
        start_time=0.0,
        end_time=2.0
    )

    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_01",
        text="Second segment",
        start_time=2.0,
        end_time=4.0
    )

    # Get segments
    segments = await realtime_segment_repository.get_by_meeting(db_session, meeting.id)

    assert len(segments) == 2
    assert segments[0].text == "First segment"
    assert segments[1].text == "Second segment"


@pytest.mark.asyncio
async def test_realtime_segments_by_speaker(client: AsyncClient, db_session):
    """Test getting segments by speaker ID."""
    # Create meeting
    meeting = Meeting(
        title="Test Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting)
    await db_session.commit()

    # Create segments for different speakers
    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="Speaker 0 segment 1",
        start_time=0.0,
        end_time=2.0
    )

    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_01",
        text="Speaker 1 segment",
        start_time=2.0,
        end_time=4.0
    )

    await realtime_segment_repository.create(
        db=db_session,
        meeting_id=meeting.id,
        speaker_id="SPEAKER_00",
        text="Speaker 0 segment 2",
        start_time=4.0,
        end_time=6.0
    )

    # Get segments for SPEAKER_00
    segments = await realtime_segment_repository.get_by_speaker(
        db_session,
        meeting.id,
        "SPEAKER_00"
    )

    assert len(segments) == 2
    assert segments[0].text == "Speaker 0 segment 1"
    assert segments[1].text == "Speaker 0 segment 2"


@pytest.mark.asyncio
async def test_meeting_mode_field(client: AsyncClient, db_session):
    """Test that meeting mode field is correctly set."""
    # Test file upload mode (default)
    meeting1 = Meeting(
        title="File Upload Meeting",
        audio_path="/path/to/audio.mp3"
    )
    db_session.add(meeting1)
    await db_session.commit()
    await db_session.refresh(meeting1)

    assert meeting1.mode == MeetingMode.FILE_UPLOAD

    # Test real-time mode
    meeting2 = Meeting(
        title="Real-time Meeting",
        audio_path="",
        mode=MeetingMode.REAL_TIME
    )
    db_session.add(meeting2)
    await db_session.commit()
    await db_session.refresh(meeting2)

    assert meeting2.mode == MeetingMode.REAL_TIME
