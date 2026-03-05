# 用户和部门功能说明

## 功能概述

本次更新添加了用户和部门的概念，实现了用户级别的数据隔离。

## 数据模型

### User（用户模型）
- `id`: 用户ID
- `username`: 用户名（唯一）
- `real_name`: 真实姓名
- `email`: 邮箱
- `phone`: 手机号
- `department_id`: 部门ID
- `position`: 职位
- `is_active`: 是否启用

### Department（部门模型）
- `id`: 部门ID
- `name`: 部门名称（唯一）
- `code`: 部门编码（唯一）
- `parent_id`: 上级部门ID
- `level`: 部门级别
- `sort_order`: 排序号
- `description`: 部门描述

### Meeting（会议模型）
- `creator_id`: 创建者ID（新增字段）

## 配置说明

在 `app/core/config.py` 中添加了以下配置：

```python
# JWT Configuration
JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
JWT_ALGORITHM: str = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

# Development Mode
DEV_MODE: bool = True
DEV_USER_ID: str = "dev-user-001"
DEV_USERNAME: str = "dev_user"
DEV_REAL_NAME: str = "开发测试用户"
```

## 中间件

### 开发模式中间件 (dev_auth_middleware)
当 `DEV_MODE` 为 `True` 时，自动注入测试用户信息到 `request.state.user`。

### JWT认证中间件 (auth_middleware)
生产环境使用，从 JWT token 中解析用户信息。

## API 端点

### 获取当前用户信息
```
GET /api/v1/users/me
```

返回当前认证用户的信息。

### 获取应用配置
```
GET /api/v1/users/config
```

返回应用配置信息，包括是否为开发模式。

### 创建会议（更新）
```
POST /api/v1/meetings/
```

现在会自动将创建者ID关联到会议记录。

## 使用方式

### 1. 运行数据库迁移

```bash
cd meeting-assistant-backend
python migrations/add_user_department.py
```

### 2. 在业务代码中获取当前用户

```python
from fastapi import Request
from app.core.security import get_current_user

async def some_endpoint(request: Request):
    # 获取当前用户信息
    user = get_current_user(request)

    if user:
        user_id = user.get("user_id")
        user_name = user.get("real_name")
        # ... 其他业务逻辑
```

### 3. 在 Service 层使用用户信息

```python
async def create_meeting(
    self,
    db: AsyncSession,
    title: str,
    audio_file: UploadFile,
    background_tasks: BackgroundTasks,
    creator_id: Optional[str] = None  # 创建者ID
) -> Meeting:
    # 使用 creator_id 创建会议
    meeting = await self.repository.create(
        db=db,
        title=title,
        audio_path=str(file_path),
        creator_id=creator_id
    )
    return meeting
```

## 开发与生产环境切换

### 开发环境（默认）
- `DEV_MODE = True`
- 自动使用测试用户，无需 JWT token
- 方便本地开发和测试

### 生产环境
- `DEV_MODE = False`
- 启用 JWT 认证
- 需要在请求头中提供有效的 JWT token：
  ```
  Authorization: Bearer <your-jwt-token>
  ```

## 数据隔离

现在所有创建的会议都会关联到创建者：

```python
# 会议响应包含创建者信息
{
    "id": "meeting-id",
    "title": "会议标题",
    "creator_id": "user-id",
    "creator": {
        "id": "user-id",
        "username": "username",
        "real_name": "真实姓名"
    },
    ...
}
```

## 后续扩展

部门信息已存储在数据库中，可以后续添加以下功能：
1. 按部门过滤会议列表
2. 部门管理接口
3. 用户权限管理
4. 部门级别的数据统计
