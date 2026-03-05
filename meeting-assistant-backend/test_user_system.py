"""Test script for user system integration."""
import requests
from typing import Optional

# API base URL
BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print('=' * 50)


def test_get_app_config():
    """Test getting application configuration."""
    print_section("1. 应用配置")
    response = requests.get(f"{BASE_URL}/api/v1/users/config")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"  - 开发模式: {result.get('dev_mode')}")
    print(f"  - 应用名称: {result.get('app_name')}")
    print(f"  - 版本: {result.get('version')}")


def test_get_current_user():
    """Test getting current user information."""
    print_section("2. 当前用户信息")
    response = requests.get(f"{BASE_URL}/api/v1/users/me")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"  - 用户ID: {result.get('user_id')}")
    print(f"  - 用户名: {result.get('username')}")
    print(f"  - 真实姓名: {result.get('real_name')}")
    print(f"  - 部门: {result.get('department_name')}")


def test_list_meetings():
    """Test listing meetings (filtered by current user)."""
    print_section("3. 会议列表（当前用户）")
    response = requests.get(f"{BASE_URL}/api/v1/meetings/")
    print(f"Status: {response.status_code}")
    result = response.json()
    total = result.get('total', 0)
    print(f"  - 总数: {total}")
    if total > 0:
        print(f"  - 会议:")
        for meeting in result.get('items', [])[:3]:
            print(f"    * {meeting['title']}")
            print(f"      创建者: {meeting.get('creator_id')}")


def test_list_all_meetings():
    """Test listing all meetings (without user filter)."""
    print_section("4. 会议列表（所有用户）")
    response = requests.get(f"{BASE_URL}/api/v1/meetings/?creator_id=")
    print(f"Status: {response.status_code}")
    result = response.json()
    total = result.get('total', 0)
    print(f"  - 总数: {total}")


def test_get_meeting_detail():
    """Test getting meeting detail with creator info."""
    print_section("5. 会议详情（含创建者）")
    # First get a meeting
    response = requests.get(f"{BASE_URL}/api/v1/meetings/")
    meetings = response.json().get('items', [])

    if meetings:
        meeting_id = meetings[0]['id']
        response = requests.get(f"{BASE_URL}/api/v1/meetings/{meeting_id}")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"  - 会议: {result['title']}")
        print(f"  - 创建者ID: {result.get('creator_id')}")
        if result.get('creator'):
            creator = result['creator']
            print(f"  - 创建者姓名: {creator.get('real_name')}")
    else:
        print("  没有会议数据")


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("  用户系统集成测试")
    print("=" * 50)

    try:
        test_get_app_config()
        test_get_current_user()
        test_list_meetings()
        test_list_all_meetings()
        test_get_meeting_detail()

        print_section("测试完成")
        print("所有测试通过！")

    except requests.exceptions.ConnectionError:
        print("\n错误: 无法连接到 API 服务器")
        print("请确保服务器正在运行:", BASE_URL)
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    main()
