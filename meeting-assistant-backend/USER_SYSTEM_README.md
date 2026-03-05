# 用户系统集成说明

## 设计说明

本应用使用外部用户系统（通过 JWT Token），只负责解析和存储用户信息，不管理用户本身。

## 核心功能

### 1. 用户信息解析
- 从 JWT Token 解析用户信息
- 开发模式可使用测试用户
- 自动将用户信息存储到本地数据库（用于关联和筛选）

### 2. 用户信息存储
User 表字段：
- `id`: 外部系统用户ID（主键）
- `username`: 用户名
- `real_name`: 真实姓名
- `email`: 邮箱
- `phone`: 手机号
- `department_id`: 部门ID
- `department_name`: 部门名称
- `position`: 职位
- `last_seen_at`: 最后访问时间

### 3. 会议关联
- Meeting 表添加 `creator_id` 字段
- 创建会议时自动关联创建者
- 可根据创建者筛选会议列表

## JWT Token 格式

外部系统应提供以下格式的 JWT Token：

```
Header: {
  "alg": "HS256",
  "typ": "JWT"
}

Payload: {
  "sub": "user-123",              # 必需：用户ID
  "username": "john_doe",         # 可选
  "real_name": "张三",            # 可选
  "email": "john@example.com",    # 可选
  "phone": "13800138000",         # 可选
  "department_id": "dept-001",    # 可选
  "department_name": "研发部",     # 可选
  "position": "工程师"             # 可选
}
```

## 配置说明

在 `app/core/config.py` 中配置：

```python
# JWT Configuration（生产环境需要修改）
JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

# Development Mode（开发测试使用）
DEV_MODE: bool = True
DEV_USER_ID: str = "dev-user-001"
DEV_USERNAME: str = "dev_user"
DEV_REAL_NAME: str = "开发测试用户"
```

## API 端点

### 获取当前用户
```
GET /api/v1/users/me
```

返回当前登录用户的信息。

### 获取应用配置
```
GET /api/v1/users/config
```

返回应用配置信息（包括是否为开发模式）。

### 会议列表（支持用户筛选）
```
GET /api/v1/meetings/?creator_id={user_id}
```

如果不传 `creator_id`，默认返回当前用户的会议。

### 创建会议
```
POST /api/v1/meetings/
```

自动关联当前用户为创建者。

## 开发与生产环境

### 开发环境
- `DEV_MODE = True`
- 使用测试用户，无需 JWT token
- 方便本地开发和测试

### 生产环境
- `DEV_MODE = False`
- 需要有效的 JWT token
- Token 应放在请求头：`Authorization: Bearer <token>`

## 数据库迁移

```bash
cd meeting-assistant-backend
python migrations/add_user_department.py
```

迁移脚本会：
1. 创建 users 表（简化版，无部门关联）
2. 添加 meetings.creator_id 字段
3. 插入测试用户数据

## 使用示例

### 前端调用示例

```typescript
// 获取当前用户
const response = await fetch('/api/v1/users/me');
const user = await response.json();
console.log(user.user_id, user.real_name);

// 获取会议列表（自动筛选当前用户）
const meetings = await fetch('/api/v1/meetings/');

// 获取特定用户的会议
const meetings = await fetch('/api/v1/users/{user_id}/meetings');
```

### 后端获取用户

```python
from app.core.security import get_current_user

async def some_endpoint(request: Request):
    user = get_current_user(request)
    if user:
        user_id = user.get("user_id")
        real_name = user.get("real_name")
        # 处理业务逻辑
```

## 注意事项

1. **用户ID作为主键**：User 表使用外部系统的用户ID作为主键，不是自增UUID
2. **自动更新**：每次请求会自动更新用户的 last_seen_at 时间
3. **部门信息**：部门信息只存储不管理，后续可根据需求扩展
4. **测试数据**：开发模式会自动创建测试用户，方便测试
