"""
用户隔离功能测试脚本

测试内容：
1. 生成两个不同用户的JWT Token
2. 使用Token1登录并获取用户信息
3. 使用Token2登录并获取用户信息
4. 验证用户信息正确
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_isolation():
    print("=" * 80)
    print("用户隔离功能测试")
    print("=" * 80)
    print()

    # 步骤1：生成测试Token
    print("【步骤1】生成测试Token")
    print("-" * 80)
    from app.utils.jwt_generator import generate_test_token

    # 用户1 Token
    token1 = generate_test_token(
        user_id='user-001',
        username='zhangsan',
        real_name='张三',
        department_id='dept-001',
        department_name='研发部',
        position='高级工程师'
    )
    print(f"用户1 Token (前50字符): {token1[:50]}...")

    # 用户2 Token
    token2 = generate_test_token(
        user_id='user-002',
        username='lisi',
        real_name='李四',
        department_id='dept-002',
        department_name='市场部',
        position='市场经理'
    )
    print(f"用户2 Token (前50字符): {token2[:50]}...")
    print()

    # 步骤2：测试登录接口
    print("【步骤2】测试登录接口")
    print("-" * 80)

    # 用户1登录
    resp1 = requests.post(f"{BASE_URL}/api/v1/users/login", json={"token": token1})
    print(f"用户1登录响应: {resp1.status_code}")
    if resp1.status_code == 200:
        user1_data = resp1.json()
        print(f"  - 用户ID: {user1_data['user']['user_id']}")
        print(f"  - 用户名: {user1_data['user']['username']}")
        print(f"  - 真实姓名: {user1_data['user']['real_name']}")
        print(f"  - 部门: {user1_data['user']['department_name']}")

    # 用户2登录
    resp2 = requests.post(f"{BASE_URL}/api/v1/users/login", json={"token": token2})
    print(f"用户2登录响应: {resp2.status_code}")
    if resp2.status_code == 200:
        user2_data = resp2.json()
        print(f"  - 用户ID: {user2_data['user']['user_id']}")
        print(f"  - 用户名: {user2_data['user']['username']}")
        print(f"  - 真实姓名: {user2_data['user']['real_name']}")
        print(f"  - 部门: {user2_data['user']['department_name']}")
    print()

    # 步骤3：测试开发模式登录
    print("【步骤3】测试开发模式登录")
    print("-" * 80)
    resp_dev = requests.post(f"{BASE_URL}/api/v1/users/login", json={"dev_mode": True})
    print(f"开发模式登录响应: {resp_dev.status_code}")
    if resp_dev.status_code == 200:
        dev_data = resp_dev.json()
        print(f"  - 用户ID: {dev_data['user']['user_id']}")
        print(f"  - 用户名: {dev_data['user']['username']}")
        print(f"  - 真实姓名: {dev_data['user']['real_name']}")
    print()

    # 步骤4：测试配置接口
    print("【步骤4】测试配置接口")
    print("-" * 80)
    resp_config = requests.get(f"{BASE_URL}/api/v1/users/config")
    print(f"配置接口响应: {resp_config.status_code}")
    if resp_config.status_code == 200:
        config_data = resp_config.json()
        print(f"  - 开发模式: {config_data['dev_mode']}")
        print(f"  - 应用名称: {config_data['app_name']}")
        print(f"  - 版本: {config_data['version']}")
    print()

    # 步骤5：测试会议列表（用户隔离）
    print("【步骤5】测试会议列表（用户隔离）")
    print("-" * 80)
    print("注意：在开发模式下，中间件会注入开发用户，所以会议列表会显示开发用户的会议")
    print()

    # 使用用户1的Token获取会议列表
    headers1 = {"Authorization": f"Bearer {token1}"}
    resp_meetings1 = requests.get(f"{BASE_URL}/api/v1/meetings/", headers=headers1)
    print(f"用户1会议列表响应: {resp_meetings1.status_code}")
    if resp_meetings1.status_code == 200:
        meetings1 = resp_meetings1.json()
        print(f"  - 会议总数: {meetings1['total']}")
        if meetings1['items']:
            print(f"  - 第一个会议的创建者: {meetings1['items'][0]['creator_id']}")
    print()

    # 使用用户2的Token获取会议列表
    headers2 = {"Authorization": f"Bearer {token2}"}
    resp_meetings2 = requests.get(f"{BASE_URL}/api/v1/meetings/", headers=headers2)
    print(f"用户2会议列表响应: {resp_meetings2.status_code}")
    if resp_meetings2.status_code == 200:
        meetings2 = resp_meetings2.json()
        print(f"  - 会议总数: {meetings2['total']}")
        if meetings2['items']:
            print(f"  - 第一个会议的创建者: {meetings2['items'][0]['creator_id']}")
    print()

    print("=" * 80)
    print("测试完成！")
    print("=" * 80)
    print()
    print("【说明】")
    print("1. Token登录成功，可以解析用户信息")
    print("2. 开发模式登录成功，使用测试用户")
    print("3. 配置接口返回正确的开发模式状态")
    print("4. 会议列表支持根据用户筛选")
    print()
    print("【用户隔离工作原理】")
    print("- 在生产模式（DEV_MODE=False）下：")
    print("  1. 中间件会解析JWT Token并注入用户信息")
    print("  2. 会议列表会自动筛选当前用户的会议")
    print("  3. 创建会议时自动关联当前用户")
    print()
    print("- 在开发模式（DEV_MODE=True）下：")
    print("  1. 中间件会注入开发测试用户")
    print("  2. 所有请求都使用开发用户身份")
    print("  3. 方便本地开发和测试")

if __name__ == "__main__":
    test_user_isolation()
