"""Tests for participant API endpoints."""
import pytest
from io import BytesIO

from app.models.meeting import Meeting, MeetingStatus
from app.models.participant import Participant


@pytest.mark.asyncio
async def test_update_participant_name(client, db_session, sample_audio_content):
    """Test updating participant display name."""
    # Create a meeting directly in DB with a participant
    meeting = Meeting(
        title="Test Meeting",
        audio_path="/tmp/test.mp3",
        status=MeetingStatus.COMPLETED
    )
    db_session.add(meeting)
    await db_session.flush()

    participant = Participant(
        meeting_id=meeting.id,
        speaker_id="speaker_1",
        display_name="说话人1"
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # Update name
    response = await client.patch(
        f"/api/v1/meetings/{meeting.id}/participants/{participant.id}",
        json={"display_name": "张三"}
    )
    assert response.status_code == 200

    result = response.json()
    assert result["display_name"] == "张三"
    assert result["speaker_id"] == "speaker_1"


@pytest.mark.asyncio
async def test_update_participant_not_found(client):
    """Test updating non-existent participant."""
    response = await client.patch(
        "/api/v1/meetings/fake-meeting/participants/fake-participant",
        json={"display_name": "New Name"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_participant_wrong_meeting(client, db_session):
    """Test updating participant with wrong meeting ID."""
    # Create two meetings
    meeting1 = Meeting(
        title="Meeting 1",
        audio_path="/tmp/test1.mp3",
        status=MeetingStatus.COMPLETED
    )
    meeting2 = Meeting(
        title="Meeting 2",
        audio_path="/tmp/test2.mp3",
        status=MeetingStatus.COMPLETED
    )
    db_session.add_all([meeting1, meeting2])
    await db_session.flush()

    # Create participant for meeting1
    participant = Participant(
        meeting_id=meeting1.id,
        speaker_id="speaker_1",
        display_name="说话人1"
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # Try to update using meeting2's ID
    response = await client.patch(
        f"/api/v1/meetings/{meeting2.id}/participants/{participant.id}",
        json={"display_name": "New Name"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_participant_empty_name(client, db_session):
    """Test updating participant with empty name."""
    # Create a meeting with participant
    meeting = Meeting(
        title="Test Meeting",
        audio_path="/tmp/test.mp3",
        status=MeetingStatus.COMPLETED
    )
    db_session.add(meeting)
    await db_session.flush()

    participant = Participant(
        meeting_id=meeting.id,
        speaker_id="speaker_1",
        display_name="说话人1"
    )
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)

    # Try to update with empty name
    response = await client.patch(
        f"/api/v1/meetings/{meeting.id}/participants/{participant.id}",
        json={"display_name": ""}
    )
    assert response.status_code == 422
