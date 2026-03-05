"""Test script for user and department functionality."""
import asyncio
import requests
from typing import Optional

# API base URL
BASE_URL = "http://localhost:8000"


def test_get_app_config():
    """Test getting application configuration."""
    response = requests.get(f"{BASE_URL}/api/v1/users/config")
    print(f"=== App Config ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_get_current_user():
    """Test getting current user information."""
    response = requests.get(f"{BASE_URL}/api/v1/users/me")
    print(f"=== Current User ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_create_meeting():
    """Test creating a meeting with user association."""
    # Prepare test data
    files = {
        'audio': ('test.mp3', b'dummy audio data', 'audio/mpeg')
    }
    data = {
        'title': '测试会议 - 用户关联'
    }

    response = requests.post(f"{BASE_URL}/api/v1/meetings/", files=files, data=data)
    print(f"=== Create Meeting ===")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response keys: {result.keys()}")
    if 'creator_id' in result:
        print(f"Creator ID: {result['creator_id']}")
    print()


def test_list_meetings():
    """Test listing meetings."""
    response = requests.get(f"{BASE_URL}/api/v1/meetings/")
    print(f"=== List Meetings ===")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Total meetings: {result.get('total', 0)}")
    for meeting in result.get('items', [])[:3]:  # Show first 3
        print(f"  - {meeting['title']} (creator_id: {meeting.get('creator_id')})")
    print()


def test_get_meeting_detail():
    """Test getting meeting detail with creator info."""
    # First get a meeting
    response = requests.get(f"{BASE_URL}/api/v1/meetings/")
    meetings = response.json().get('items', [])

    if meetings:
        meeting_id = meetings[0]['id']
        response = requests.get(f"{BASE_URL}/api/v1/meetings/{meeting_id}")
        print(f"=== Meeting Detail ===")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Meeting: {result['title']}")
        if 'creator' in result and result['creator']:
            print(f"Creator: {result['creator']}")
        else:
            print(f"Creator ID: {result.get('creator_id')}")
        print()


def main():
    """Run all tests."""
    print("Testing User and Department Functionality")
    print("=" * 50)
    print()

    try:
        test_get_app_config()
        test_get_current_user()
        test_list_meetings()
        test_get_meeting_detail()
        # test_create_meeting()  # Uncomment to test meeting creation

        print("=" * 50)
        print("All tests completed!")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Please make sure the server is running at", BASE_URL)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
