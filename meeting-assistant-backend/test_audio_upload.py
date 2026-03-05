"""测试真实音频文件上传"""
import requests
import os

BASE_URL = "http://127.0.0.1:7654"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwMSIsInVzZXJuYW1lIjoiemhhbmdzYW4iLCJyZWFsX25hbWUiOiJcdTVmMjBcdTRlMDkiLCJkZXBhcnRtZW50X2lkIjoiZGVwdC0wMDEiLCJkZXBhcnRtZW50X25hbWUiOiJcdTc4MTRcdTUzZDFcdTkwZTgiLCJwb3NpdGlvbiI6Ilx1OWFkOFx1N2VhN1x1NWRlNVx1N2EwYlx1NWUwOCIsImlhdCI6MTc3MjY5ODUwMCwiZXhwIjoxODA0MjM0NTAwfQ.bZbVagpEd07W5Sdi_9SsztnmNyQFryizbY6-qhT0YOo"

def test_upload_audio():
    """使用真实音频文件测试上传"""
    print("Testing audio file upload...")

    # 使用已有的音频文件
    audio_file = "uploads/031722be-7014-4a0f-9438-83940086421f.mp3"

    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return False

    file_size = os.path.getsize(audio_file)
    print(f"Audio file: {audio_file} ({file_size} bytes)")

    try:
        with open(audio_file, "rb") as f:
            files = {"audio": (os.path.basename(audio_file), f, "audio/mpeg")}
            data = {"title": "测试会议 - 音频上传"}

            response = requests.post(
                f"{BASE_URL}/api/v1/meetings/",
                params={"token": TOKEN},
                files=files,
                data=data,
                timeout=30
            )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            print(f"Success!")
            print(f"  Meeting ID: {result.get('id')}")
            print(f"  Title: {result.get('title')}")
            print(f"  Creator ID: {result.get('creator_id')}")
            print(f"  Status: {result.get('status')}")
            print(f"  Progress: {result.get('progress')}%")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_meeting_list():
    """获取会议列表"""
    print("\nGetting meeting list...")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/meetings/",
            params={"token": TOKEN},
            timeout=5
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"Total meetings: {data.get('total', 0)}")
            for meeting in data.get('items', [])[:5]:
                print(f"  - {meeting.get('title')} (creator: {meeting.get('creator_id')})")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Exception: {e}")
        return False


if __name__ == "__main__":
    print("="*50)
    print("Audio Upload Test")
    print("="*50)
    print()

    # 上传音频
    upload_result = test_upload_audio()

    # 获取列表
    list_result = test_get_meeting_list()

    print()
    print("="*50)
    if upload_result and list_result:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED")
    print("="*50)
