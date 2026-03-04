"""Test script to compare httpx with curl for voice separation API."""
import asyncio
import httpx
from pathlib import Path

# Test configuration
AUDIO_FILE = "uploads/89e57f5b-fa79-4585-979e-bad4fd250e28.mp3"
API_URL = "http://192.168.0.100:40901/recognize"

async def test_with_httpx():
    """Test using httpx like the separation service does."""
    print("=" * 60)
    print("Testing with httpx (like separation_service.py)")
    print("=" * 60)

    file_path = Path(AUDIO_FILE)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    # Get MIME type
    file_ext = file_path.suffix.lower()
    mime_type = "audio/mpeg" if file_ext == ".mp3" else "audio/wav"
    print(f"File: {file_path.name}")
    print(f"MIME type: {mime_type}")
    print(f"API URL: {API_URL}")

    # Configure timeout
    timeout = httpx.Timeout(30.0, connect=30.0, read=300.0, write=60.0)

    try:
        async with httpx.AsyncClient(timeout=timeout, proxy=None) as client:
            with open(file_path, 'rb') as f:
                files = {"file": (file_path.name, f, mime_type)}
                data = {"enable_diarization": True}

                print("\nSending request...")
                response = await client.post(
                    API_URL,
                    files=files,
                    data=data
                )

                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"Code: {result.get('code')}")
                    print(f"Message: {result.get('message')}")
                    data_obj = result.get('data', {})
                    print(f"Speakers: {data_obj.get('speaker_count')}")
                    print(f"Segments: {data_obj.get('segment_count')}")
                    print("\n*** httpx test PASSED ***")
                else:
                    print(f"Response: {response.text[:500]}")
                    print("\n*** httpx test FAILED ***")

    except Exception as e:
        print(f"\n*** Error: {e} ***")

async def test_different_approaches():
    """Test different httpx approaches."""
    print("\n" + "=" * 60)
    print("Testing different httpx approaches")
    print("=" * 60)

    file_path = Path(AUDIO_FILE)
    file_ext = file_path.suffix.lower()

    # Read file content
    with open(file_path, 'rb') as f:
        file_content = f.read()

    approaches = [
        ("Standard multipart", None),
        ("With explicit headers", {"Content-Type": "multipart/form-data"}),
    ]

    for name, headers in approaches:
        print(f"\n--- {name} ---")
        timeout = httpx.Timeout(30.0, connect=30.0, read=300.0)

        try:
            async with httpx.AsyncClient(timeout=timeout, proxy=None) as client:
                files = {"file": (file_path.name, file_content, "audio/mpeg")}
                data = {"enable_diarization": "true"}

                response = await client.post(
                    API_URL,
                    files=files,
                    data=data,
                    headers=headers
                )

                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print("SUCCESS!")
                    break
                else:
                    print(f"Failed: {response.text[:200]}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_httpx())
    asyncio.run(test_different_approaches())
