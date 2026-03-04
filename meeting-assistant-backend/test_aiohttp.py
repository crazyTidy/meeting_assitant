"""Test aiohttp version of voice separation."""
import asyncio
import aiohttp
from pathlib import Path

AUDIO_FILE = "uploads/89e57f5b-fa79-4585-979e-bad4fd250e28.mp3"
API_URL = "http://192.168.0.100:40901/recognize"

async def test_with_aiohttp():
    """Test using aiohttp."""
    print("=" * 60)
    print("Testing with aiohttp")
    print("=" * 60)

    file_path = Path(AUDIO_FILE)
    file_ext = file_path.suffix.lower()
    mime_type = "audio/mpeg" if file_ext == ".mp3" else "audio/wav"

    print(f"File: {file_path.name}")
    print(f"MIME type: {mime_type}")
    print(f"API URL: {API_URL}")

    timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_read=300)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            with open(file_path, 'rb') as f:
                file_content = f.read()

                data = aiohttp.FormData()
                data.add_field(
                    'file',
                    file_content,
                    filename=file_path.name,
                    content_type=mime_type
                )
                data.add_field('enable_diarization', 'true')

                print("\nSending request...")
                async with session.post(API_URL, data=data) as response:
                    print(f"Status: {response.status}")

                    if response.status == 200:
                        result = await response.json()
                        print(f"Code: {result.get('code')}")
                        print(f"Message: {result.get('message')}")
                        data_obj = result.get('data', {})
                        print(f"Speakers: {data_obj.get('speaker_count')}")
                        print(f"Segments: {data_obj.get('segment_count')}")
                        print("\n*** aiohttp test PASSED ***")
                        return True
                    else:
                        text = await response.text()
                        print(f"Response: {text[:500]}")
                        print("\n*** aiohttp test FAILED ***")
                        return False

    except Exception as e:
        print(f"\n*** Error: {e} ***")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_with_aiohttp())
    exit(0 if result else 1)
