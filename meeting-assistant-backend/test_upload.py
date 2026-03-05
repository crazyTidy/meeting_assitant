"""测试文件上传功能"""
import requests
import os

BASE_URL = "http://127.0.0.1:7654"

# Token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTAwMSIsInVzZXJuYW1lIjoiemhhbmdzYW4iLCJyZWFsX25hbWUiOiJcdTVmMjBcdTRlMDkiLCJkZXBhcnRtZW50X2lkIjoiZGVwdC0wMDEiLCJkZXBhcnRtZW50X25hbWUiOiJcdTc4MTRcdTUzZDFcdTkwZTgiLCJwb3NpdGlvbiI6Ilx1OWFkOFx1N2VhN1x1NWRlNVx1N2EwYlx1NWUwOCIsImlhdCI6MTc3MjY5ODUwMCwiZXhwIjoxODA0MjM0NTAwfQ.bZbVagpEd07W5Sdi_9SsztnmNyQFryizbY6-qhT0YOo"

def test_health():
    """测试健康检查"""
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        return True
    except Exception as e:
        print(f"   错误: {e}")
        return False


def test_get_current_user():
    """测试获取当前用户"""
    print("\n2. 测试获取当前用户...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/users/me",
            params={"token": TOKEN},
            timeout=2
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   用户: {response.json()}")
            return True
        else:
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"   异常: {e}")
        return False


def test_list_meetings():
    """测试获取会议列表"""
    print("\n3. 测试获取会议列表...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/meetings/",
            params={"token": TOKEN},
            timeout=2
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   会议数量: {data.get('total', 0)}")
            return True
        else:
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"   异常: {e}")
        return False


def test_upload_meeting():
    """测试上传会议"""
    print("\n4. 测试上传会议...")

    # 创建测试文件
    test_file = "test_audio.txt"
    with open(test_file, "w") as f:
        f.write("test audio content")

    try:
        with open(test_file, "rb") as f:
            files = {"audio": (test_file, f, "audio/mpeg")}
            data = {"title": "测试会议"}

            response = requests.post(
                f"{BASE_URL}/api/v1/meetings/",
                params={"token": TOKEN},
                files=files,
                data=data,
                timeout=10
            )

        print(f"   状态码: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"   会议ID: {result.get('id')}")
            print(f"   标题: {result.get('title')}")
            print(f"   创建者ID: {result.get('creator_id')}")
            return True
        else:
            print(f"   错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"   异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def main():
    print("="*50)
    print("文件上传功能自测")
    print("="*50)

    results = []

    # 运行测试
    results.append(("健康检查", test_health()))
    results.append(("获取用户", test_get_current_user()))
    results.append(("会议列表", test_list_meetings()))
    results.append(("上传会议", test_upload_meeting()))

    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总")
    print("="*50)
    for name, result in results:
        status = "通过" if result else "失败"
        print(f"  {name}: {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()
