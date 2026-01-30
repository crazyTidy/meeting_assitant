"""Tests for meeting API endpoints."""
import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_meeting(client, sample_audio_content):
    """Test creating a new meeting."""
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    data = {"title": "Test Meeting"}

    response = await client.post("/api/v1/meetings/", files=files, data=data)
    assert response.status_code == 201

    result = response.json()
    assert result["title"] == "Test Meeting"
    assert result["status"] == "pending"
    assert "id" in result


@pytest.mark.asyncio
async def test_create_meeting_invalid_format(client):
    """Test creating meeting with invalid audio format."""
    files = {
        "audio": ("test.txt", BytesIO(b"not audio"), "text/plain")
    }
    data = {"title": "Test Meeting"}

    response = await client.post("/api/v1/meetings/", files=files, data=data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_meeting_empty_title(client, sample_audio_content):
    """Test creating meeting with empty title."""
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    data = {"title": ""}

    response = await client.post("/api/v1/meetings/", files=files, data=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_meetings_empty(client):
    """Test getting meeting list when empty."""
    response = await client.get("/api/v1/meetings/")
    assert response.status_code == 200

    result = response.json()
    assert result["items"] == []
    assert result["total"] == 0


@pytest.mark.asyncio
async def test_get_meetings_with_data(client, sample_audio_content):
    """Test getting meeting list with data."""
    # Create a meeting first
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    data = {"title": "Test Meeting"}
    await client.post("/api/v1/meetings/", files=files, data=data)

    # Get list
    response = await client.get("/api/v1/meetings/")
    assert response.status_code == 200

    result = response.json()
    assert len(result["items"]) == 1
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_get_meetings_with_search(client, sample_audio_content):
    """Test searching meetings."""
    # Create two meetings
    files1 = {
        "audio": ("test1.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    await client.post("/api/v1/meetings/", files=files1, data={"title": "Product Review"})

    files2 = {
        "audio": ("test2.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    await client.post("/api/v1/meetings/", files=files2, data={"title": "Tech Discussion"})

    # Search for "Product"
    response = await client.get("/api/v1/meetings/?search=Product")
    assert response.status_code == 200

    result = response.json()
    assert len(result["items"]) == 1
    assert result["items"][0]["title"] == "Product Review"


@pytest.mark.asyncio
async def test_get_meetings_pagination(client, sample_audio_content):
    """Test meeting list pagination."""
    # Create 5 meetings
    for i in range(5):
        files = {
            "audio": (f"test{i}.mp3", BytesIO(sample_audio_content), "audio/mpeg")
        }
        await client.post("/api/v1/meetings/", files=files, data={"title": f"Meeting {i}"})

    # Get first page with size 2
    response = await client.get("/api/v1/meetings/?page=1&size=2")
    assert response.status_code == 200

    result = response.json()
    assert len(result["items"]) == 2
    assert result["total"] == 5
    assert result["pages"] == 3


@pytest.mark.asyncio
async def test_get_meeting_detail(client, sample_audio_content):
    """Test getting meeting detail."""
    # Create a meeting
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    create_response = await client.post(
        "/api/v1/meetings/",
        files=files,
        data={"title": "Test Meeting"}
    )
    meeting_id = create_response.json()["id"]

    # Get detail
    response = await client.get(f"/api/v1/meetings/{meeting_id}")
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == meeting_id
    assert result["title"] == "Test Meeting"
    assert "participants" in result
    assert "summary" in result


@pytest.mark.asyncio
async def test_get_meeting_not_found(client):
    """Test getting non-existent meeting."""
    response = await client.get("/api/v1/meetings/non-existent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_meeting_status(client, sample_audio_content):
    """Test getting meeting status."""
    # Create a meeting
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    create_response = await client.post(
        "/api/v1/meetings/",
        files=files,
        data={"title": "Test Meeting"}
    )
    meeting_id = create_response.json()["id"]

    # Get status
    response = await client.get(f"/api/v1/meetings/{meeting_id}/status")
    assert response.status_code == 200

    result = response.json()
    assert result["id"] == meeting_id
    assert "status" in result
    assert "progress" in result
    assert "message" in result


@pytest.mark.asyncio
async def test_delete_meeting(client, sample_audio_content):
    """Test deleting a meeting."""
    # Create a meeting
    files = {
        "audio": ("test_audio.mp3", BytesIO(sample_audio_content), "audio/mpeg")
    }
    create_response = await client.post(
        "/api/v1/meetings/",
        files=files,
        data={"title": "Test Meeting"}
    )
    meeting_id = create_response.json()["id"]

    # Delete
    response = await client.delete(f"/api/v1/meetings/{meeting_id}")
    assert response.status_code == 204

    # Verify deleted
    response = await client.get(f"/api/v1/meetings/{meeting_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_meeting_not_found(client):
    """Test deleting non-existent meeting."""
    response = await client.delete("/api/v1/meetings/non-existent-id")
    assert response.status_code == 404
