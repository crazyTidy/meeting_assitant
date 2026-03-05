"""JWT Token generation utility for testing."""
import jwt
from datetime import datetime, timedelta
from app.core.config import settings


def generate_test_token(
    user_id: str,
    username: str = None,
    real_name: str = None,
    department_id: str = None,
    department_name: str = None,
    position: str = None,
    expires_in_days: int = 365
) -> str:
    """
    生成测试用的 JWT Token。

    Args:
        user_id: 用户ID（必需）
        username: 用户名
        real_name: 真实姓名
        department_id: 部门ID
        department_name: 部门名称
        position: 职位
        expires_in_days: 过期天数

    Returns:
        JWT Token 字符串
    """
    payload = {
        "sub": user_id,
        "username": username,
        "real_name": real_name,
        "department_id": department_id,
        "department_name": department_name,
        "position": position,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expires_in_days)
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token


def validate_token(token: str) -> dict | None:
    """
    验证并解析 JWT Token，返回用户信息。

    与 decode_token 的区别是，这个函数在验证失败时返回 None 而不是抛出异常。

    Args:
        token: JWT Token 字符串

    Returns:
        解析后的 payload 字典，包含 user_id 等字段；验证失败时返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # 将 JWT 标准的 sub 字段映射为 user_id
        if "sub" in payload:
            payload["user_id"] = payload["sub"]
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None


def decode_token(token: str) -> dict:
    """
    解析 JWT Token。

    Args:
        token: JWT Token 字符串

    Returns:
        解析后的 payload 字典
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token 已过期")
    except jwt.InvalidTokenError:
        raise ValueError("无效的 Token")


def print_test_tokens():
    """打印测试用的 Token 信息。"""
    print("\n" + "=" * 70)
    print("  测试用 JWT Token")
    print("=" * 70)

    # Token 1: 研发部 - 张三
    token1 = generate_test_token(
        user_id="user-001",
        username="zhangsan",
        real_name="张三",
        department_id="dept-001",
        department_name="研发部",
        position="高级工程师"
    )
    print("\n【用户 1】研发部 - 张三")
    print("-" * 70)
    print(f"用户ID: user-001")
    print(f"用户名: zhangsan")
    print(f"真实姓名: 张三")
    print(f"部门: 研发部")
    print(f"职位: 高级工程师")
    print(f"\nToken:")
    print(token1)

    # Token 2: 市场部 - 李四
    token2 = generate_test_token(
        user_id="user-002",
        username="lisi",
        real_name="李四",
        department_id="dept-002",
        department_name="市场部",
        position="市场经理"
    )
    print("\n" + "=" * 70)
    print("\n【用户 2】市场部 - 李四")
    print("-" * 70)
    print(f"用户ID: user-002")
    print(f"用户名: lisi")
    print(f"真实姓名: 李四")
    print(f"部门: 市场部")
    print(f"职位: 市场经理")
    print(f"\nToken:")
    print(token2)

    print("\n" + "=" * 70)
    print("\n📝 使用说明:")
    print("-" * 70)
    print("1. 在请求头中添加:")
    print("   Authorization: Bearer <token>")
    print("\n2. 前端示例:")
    print("   fetch('/api/v1/users/me', {")
    print("     headers: { 'Authorization': 'Bearer " + token1[:20] + "...' }")
    print("   })")
    print("\n3. 或在浏览器开发者工具中:")
    print("   - 打开 Console")
    print("   - localStorage.setItem('token', '" + token1[:20] + "...')")
    print("\n4. 使用不同 Token 创建的会议会关联到不同用户")
    print("=" * 70 + "\n")

    return {
        "user1": {
            "info": {
                "user_id": "user-001",
                "username": "zhangsan",
                "real_name": "张三",
                "department_id": "dept-001",
                "department_name": "研发部",
                "position": "高级工程师"
            },
            "token": token1
        },
        "user2": {
            "info": {
                "user_id": "user-002",
                "username": "lisi",
                "real_name": "李四",
                "department_id": "dept-002",
                "department_name": "市场部",
                "position": "市场经理"
            },
            "token": token2
        }
    }


if __name__ == "__main__":
    tokens = print_test_tokens()

    # 保存到文件方便复制
    with open("test_tokens.txt", "w", encoding="utf-8") as f:
        f.write("# 测试用 JWT Token\n\n")
        f.write("## 用户1: 张三 (研发部)\n")
        f.write(f"```\n{tokens['user1']['token']}\n```\n\n")
        f.write("## 用户2: 李四 (市场部)\n")
        f.write(f"```\n{tokens['user2']['token']}\n```\n")
        f.write("\n## 使用方式\n")
        f.write("在请求头中添加: `Authorization: Bearer <token>`\n")

    print("✅ Token 已保存到 test_tokens.txt 文件")
