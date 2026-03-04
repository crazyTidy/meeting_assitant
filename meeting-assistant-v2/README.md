# Meeting Assistant V2

会议助手后端 API - 音频处理、人声分离、AI 纪要生成

## 项目简介

Meeting Assistant V2 是一个基于 FastAPI 的企业级后端应用，用于处理会议音频文件，实现以下核心功能：

1. **音频上传与处理** - 支持多种音频格式上传（MP3、WAV、M4A、FLAC、OGG）
2. **人声分离** - 调用第三方 API 进行说话人分离和时间轴分析
3. **语音转文字** - 将音频转换为文本
4. **AI 纪要生成** - 使用智谱 AI GLM 模型自动生成会议纪要
5. **用户系统集成** - 集成主应用的用户、权限和部门服务

## 项目架构

本项目基于 `fastapi_module_template` 模板构建，采用分层架构设计：

```
meeting-assistant-v2/
├── models/              # 数据库 ORM 模型
│   ├── meeting_model.py      # 会议模型
│   ├── participant_model.py  # 参与者模型
│   ├── speaker_segment_model.py  # 说话片段模型
│   ├── merged_segment_model.py   # 合并片段模型
│   ├── summary_model.py      # 纪要模型
│   └── database.py           # 数据库连接
├── items/               # Pydantic 数据结构（API 请求/响应）
│   └── meeting_item.py
├── repositories/        # 数据访问层
│   └── meeting_repository.py
├── services/            # 业务逻辑层
│   ├── meeting_service.py     # 会议服务
│   ├── separation_service.py  # 人声分离服务
│   ├── asr_service.py         # ASR 服务
│   └── llm_service.py         # LLM 服务
├── routers/             # API 路由
│   └── meeting_router.py
├── tasks/               # 后台任务
│   ├── processor.py      # 会议处理任务
│   └── regenerator.py    # 纪要重新生成任务
├── utils/               # 工具类
│   └── audio_util.py     # 音频工具
├── settings/            # 配置
│   └── environment_config.py
└── app.py               # 应用入口
```

## 技术栈

- **Web 框架**: FastAPI 0.109+
- **数据库 ORM**: SQLAlchemy 2.0+
- **数据库驱动**: aiosqlite (SQLite) / asyncpg (PostgreSQL)
- **HTTP 客户端**: aiohttp, httpx
- **AI 服务**: 智谱 AI GLM

## 安装部署

### 1. 安装依赖

```bash
cd meeting-assistant-v2
python pip_requirements.py
```

### 2. 配置环境变量

编辑 `scripts/environment.sh` (Linux/Mac) 或 `scripts/environment.bat` (Windows)：

```bash
# 基础配置
HOST=0.0.0.0
PORT=8000
RELOAD=1
WORKERS=1

# 数据库配置（默认使用 SQLite）
SQLALCHEMY_DATABASE_URL=sqlite+aiosqlite:///./meeting_assistant.db

# 会议助手配置
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# API 配置
ZHIPU_API_KEY=your_zhipu_api_key_here
SEPARATION_API_URL=http://192.168.0.100:40901/recognize
SEPARATION_API_KEY=
ASR_API_URL=
ASR_API_KEY=
```

### 3. 启动项目

**Linux/Mac:**
```bash
source scripts/environment.sh
chmod +x scripts/start.sh
./scripts/start.sh
```

**Windows:**
```bash
scripts\\environment.bat
scripts\\start.bat
```

### 4. 访问 API 文档

启动后访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

## API 端点

### 会议管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/meetings/` | 上传音频并创建会议 |
| GET | `/meetings/` | 获取会议列表 |
| GET | `/meetings/{meeting_id}` | 获取会议详情 |
| GET | `/meetings/{meeting_id}/status` | 获取处理状态 |
| DELETE | `/meetings/{meeting_id}` | 删除会议 |
| GET | `/meetings/{meeting_id}/audio` | 下载音频文件 |
| PATCH | `/meetings/{meeting_id}/summary` | 更新会议纪要 |
| POST | `/meetings/{meeting_id}/regenerate-summary` | 重新生成纪要 |

### 健康检查

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/health` | 服务健康检查 |

## 处理流程

会议处理分为两个阶段，第二阶段失败不影响第一阶段的数据：

### 阶段1：人声分离 (10%-50%)

1. 初始化 (10%)
2. 调用人声分离 API (10%-40%)
3. 保存参与者和时间轴数据 (40%-50%)
4. **里程碑：人声分离完成 (50%)**

### 阶段2：纪要生成 (50%-100%)

1. 调用 LLM 生成纪要 (50%-90%)
2. 保存纪要 (90%-99%)
3. **里程碑：处理完成 (100%)**

## 开发说明

### 相对引用规范

开发时使用相对引用：

```python
# 服务层引用
from ..models.meeting_model import Meeting
from ..repositories.meeting_repository import meeting_repository
from ..items.meeting_item import MeetingResponseItem

# 跨层引用
from meeting_assistant_v2.models.database import AsyncSessionLocal
```

### 数据库操作

使用 `AsyncSessionLocal` 进行数据库操作：

```python
async with AsyncSessionLocal() as db:
    meeting = await meeting_repository.get(db, meeting_id)
    await db.commit()
```

### 后台任务

使用 FastAPI 的 `BackgroundTasks` 启动后台处理：

```python
background_tasks.add_task(
    process_meeting_task,
    meeting_id=meeting.id
)
```

## 编译打包（可选）

如需编译保护代码：

**Linux/Mac:**
```bash
chmod +x scripts/compile.sh
./scripts/compile.sh
```

**Windows:**
```bash
scripts\\compile.bat
```

编译结果保存在 `builds/` 目录。

## 用户系统集成

本项目已集成用户系统接口封装，可通过 `utils.clients` 模块访问主应用的用户、权限和部门服务。

### 功能特性

- **UserClient**: 用户信息接口（获取用户详情、用户列表、搜索用户）
- **PermissionClient**: 权限验证接口（检查权限、获取用户权限和角色）
- **DepartmentClient**: 部门树接口（获取部门树、部门成员、用户部门）

### 使用示例

```python
from meeting_assistant_v2.utils.clients import UserClient, PermissionClient, DepartmentClient

# 获取用户信息
user_client = UserClient()
user_info = await user_client.get_user_info(user_id="123")

# 检查权限
permission_client = PermissionClient()
has_permission = await permission_client.check_permission(
    user_id="123",
    resource="meeting:create",
    action="create"
)

# 获取部门树
department_client = DepartmentClient()
dept_tree = await department_client.get_department_tree()
```

### 配置

需要配置环境变量：

```bash
# 用户服务接口地址
USER_SERVICE_URL=http://localhost:8001

# 权限服务接口地址
PERMISSION_SERVICE_URL=http://localhost:8002

# 部门服务接口地址
DEPARTMENT_SERVICE_URL=http://localhost:8003

# 接口超时时间（秒）
USER_REQUEST_TIMEOUT=30
```

## 注意事项

1. **禁止 pathlib**: 模板不支持 pathlib 库，使用 `os.path` 代替
2. **JSON 格式**: 禁止使用 `json.loads` 解析列表，所有 json 数据必须是字典
3. **await 返回**: 禁止在 `@router` 监听函数中直接返回 `await`
4. **APIRouter**: 使用 APIRouter 构建子路由

## 许可证

MIT License
