# Meeting Assistant

智能会议助手应用 - 自动生成会议纪要

## 项目概述

Meeting Assistant 是一个面向个人用户的会议助手应用，支持音频上传、人声分离、大模型会议纪要自动生成等功能。

### 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Pinia + Tailwind CSS
- **后端**: FastAPI + SQLAlchemy + SQLite
- **大模型**: 智谱 GLM API
- **人声分离**: 第三方 API

## 项目结构

```
cc/
├── meeting-assistant-backend/     # 后端项目
│   ├── app/
│   │   ├── api/v1/               # API 端点
│   │   ├── core/                 # 核心配置
│   │   ├── models/               # 数据模型
│   │   ├── repositories/         # 数据访问层
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # 业务逻辑层
│   │   └── tasks/                # 后台任务
│   ├── tests/                    # 测试用例
│   └── uploads/                  # 上传文件存储
│
├── meeting-assistant-frontend/    # 前端项目
│   └── src/
│       ├── api/                  # API 调用
│       ├── components/           # Vue 组件
│       ├── router/               # 路由配置
│       ├── stores/               # Pinia 状态管理
│       ├── types/                # TypeScript 类型
│       └── views/                # 页面视图
│
└── docs/                         # 文档
    └── plans/                    # 设计文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 后端启动

```bash
cd meeting-assistant-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
cd meeting-assistant-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 即可使用应用。

## API 文档

启动后端后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/meetings/ | 上传音频并创建会议 |
| GET | /api/v1/meetings/ | 获取会议列表 |
| GET | /api/v1/meetings/{id} | 获取会议详情 |
| GET | /api/v1/meetings/{id}/status | 获取处理状态 |
| DELETE | /api/v1/meetings/{id} | 删除会议 |
| PATCH | /api/v1/meetings/{id}/participants/{pid} | 修改说话人名称 |

## 功能特性

### 已实现

- [x] 音频文件上传（支持 MP3, WAV, M4A, FLAC, OGG）
- [x] 会议列表展示、搜索、分页
- [x] 会议详情查看（左右分栏布局）
- [x] 说话人名称修改
- [x] 会议纪要 Markdown 渲染
- [x] 处理状态轮询
- [x] 会议删除

### 待实现

- [ ] 实际人声分离 API 集成
- [ ] 实际智谱 GLM API 集成
- [ ] 音频播放功能
- [ ] 会议纪要导出（PDF/Word）

## 配置说明

### 后端环境变量

```env
# 应用配置
APP_NAME=Meeting Assistant
DEBUG=true

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./meeting_assistant.db

# 文件上传
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=104857600  # 100MB

# 外部 API
ZHIPU_API_KEY=your_zhipu_api_key_here
SEPARATION_API_KEY=your_separation_api_key_here
SEPARATION_API_URL=https://api.example.com/separation
```

## 测试

```bash
cd meeting-assistant-backend

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/
```

## 开发说明

### 代码规范

- 后端使用 Python 类型注解
- 前端使用 TypeScript 严格模式
- 遵循 RESTful API 设计规范

### 提交规范

使用 Conventional Commits 规范：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 许可证

MIT License
