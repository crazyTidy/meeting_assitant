"""Test using requests library instead of httpx."""
import requests
from pathlib import Path

# Test configuration
AUDIO_FILE = "uploads/89e57f5b-fa79-4585-979e-bad4fd250e28.mp3"
API_URL = "http://192.168.0.100:40901/recognize"

def test_with_requests():
    """Test using requests library."""
    print("=" * 60)
    print("Testing with requests library")
    print("=" * 60)

    file_path = Path(AUDIO_FILE)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    file_ext = file_path.suffix.lower()
    mime_type = "audio/mpeg" if file_ext == ".mp3" else "audio/wav"
    print(f"File: {file_path.name}")
    print(f"MIME type: {mime_type}")
    print(f"API URL: {API_URL}")

    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, mime_type)}
            data = {"enable_diarization": "true"}

            print("\nSending request...")
            response = requests.post(
                API_URL,
                files=files,
                data=data,
                timeout=300
            )

            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Code: {result.get('code')}")
                print(f"Message: {result.get('message')}")
                data_obj = result.get('data', {})
                print(f"Speakers: {data_obj.get('speaker_count')}")
                print(f"Segments: {data_obj.get('segment_count')}")
                print("\n*** requests test PASSED ***")
                return True
            else:
                print(f"Response: {response.text[:500]}")
                print("\n*** requests test FAILED ***")
                return False

    except Exception as e:
        print(f"\n*** Error: {e} ***")
        return False

if __name__ == "__main__":
    test_with_requests()
