# 会议助手应用设计文档

> 创建日期：2026-01-29

## 概述

一个面向个人用户的会议助手应用，支持音频上传、人声分离、大模型会议纪要自动生成等功能。

### 技术栈

- **前端**：Vue 3 + TypeScript + Vite
- **后端**：FastAPI + SQLAlchemy + SQLite
- **大模型**：智谱 GLM API
- **人声分离**：第三方 API

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Vue3 前端 (Vite)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────────────┐ │
│  │上传页面   │ │会议列表   │ │         会议详情                 │ │
│  │          │ │          │ │  ┌──────────┬─────────────────┐  │ │
│  │          │ │          │ │  │ 人员列表 │    会议纪要     │  │ │
│  │          │ │          │ │  │ (左侧)   │    (右侧)       │  │ │
│  │          │ │          │ │  └──────────┴─────────────────┘  │ │
│  └──────────┘ └──────────┘ └──────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FastAPI 后端                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐      │
│  │ 会议 API     │ │ 文件上传 API  │ │ 任务状态轮询 API    │      │
│  └──────────────┘ └──────────────┘ └──────────────────────┘      │
│                              │                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │              后台任务处理器 (BackgroundTasks)              │    │
│  │   ┌────────────┐         ┌────────────────────────────┐  │    │
│  │   │ 人声分离   │────────→│ 智谱GLM 会议纪要生成       │  │    │
│  │   │ (分离说话人)│         │ (基于分离后的音频)         │  │    │
│  │   └────────────┘         └────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌────────────┐      ┌────────────┐      ┌────────────┐
    │ SQLite DB  │      │ 本地文件   │      │ 外部API    │
    │ (元数据)   │      │ (音频存储) │      │ (智谱GLM)  │
    └────────────┘      └────────────┘      └────────────┘
```

### 核心流程

1. 用户上传音频 → 保存文件 → 创建会议记录 → 返回会议ID
2. 后台任务：人声分离API → 智谱GLM直接处理音频生成纪要
3. 前端轮询任务状态 → 处理完成后展示结果
4. 用户可在详情页修改说话人名称

## 数据模型

```python
# 会议记录表 (meetings)
class Meeting:
    id: str (UUID)              # 主键
    title: str                   # 会议标题
    audio_path: str             # 原始音频文件路径
    status: str                 # pending/processing/completed/failed
    created_at: datetime        # 创建时间
    updated_at: datetime        # 更新时间
    duration: int               # 音频时长(秒)，可空

# 会议参与者表 (participants)
class Participant:
    id: str (UUID)              # 主键
    meeting_id: str (FK)        # 关联会议ID
    speaker_id: str             # 说话人编号(如 speaker_1)
    display_name: str           # 显示名称(用户可修改)
    voice_segment_path: str     # 分离后的音频片段路径，可空

# 会议纪要表 (summaries)
class Summary:
    id: str (UUID)              # 主键
    meeting_id: str (FK)        # 关联会议ID
    content: str                # 纪要内容(Markdown格式)
    raw_response: str           # 大模型原始响应，可空
    generated_at: datetime      # 生成时间
```

## API 接口设计

```
基础路径: /api/v1

【会议相关】
POST   /meetings                    # 上传音频并创建会议
GET    /meetings                    # 获取会议列表(支持搜索/分页)
GET    /meetings/{id}               # 获取会议详情
DELETE /meetings/{id}               # 删除会议

【参与者相关】
PATCH  /meetings/{id}/participants/{pid}  # 修改说话人名称

【任务状态】
GET    /meetings/{id}/status        # 获取处理状态(轮询用)
```

### 请求/响应示例

```
POST /meetings
Request: multipart/form-data
  - title: "周一产品评审会"
  - audio: <file>
Response: { id, title, status: "pending", created_at }

GET /meetings?search=产品&page=1&size=10
Response: { items: [...], total, page, size }

GET /meetings/{id}/status
Response: { status: "processing", progress: 50, message: "正在生成纪要..." }

PATCH /meetings/{id}/participants/{pid}
Request: { display_name: "张三" }
Response: { id, speaker_id, display_name }
```

### 设计原则

- RESTful 风格
- 使用 JSON 响应
- 统一错误格式：`{ error: { code, message } }`
- 分页采用 offset/limit 模式

## 前端页面设计

### 路由设计

```
/                   → 重定向到 /meetings
/upload             → 上传页面
/meetings           → 会议列表页
/meetings/:id       → 会议详情页
```

### 上传页面 (/upload)

- 拖拽或点击上传音频
- 支持 mp3, wav, m4a 格式
- 输入会议标题
- 开始处理按钮

### 会议列表页 (/meetings)

- 搜索框
- 会议卡片列表（标题、时间、状态、操作按钮）
- 分页
- 新建会议入口

### 会议详情页 (/meetings/:id) - 讯飞风格

- 左右等高布局
- 左侧：参会人员列表，可点击编辑名称
- 右侧：会议纪要内容，Markdown 渲染

### 组件设计

- `AudioUploader`: 拖拽上传组件
- `MeetingCard`: 会议列表卡片
- `ParticipantList`: 参会人员列表(可编辑名称)
- `SummaryViewer`: 纪要展示(Markdown渲染)
- `StatusBadge`: 状态徽章

## 目录结构

### 后端 (meeting-assistant-backend)

```
meeting-assistant-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # SQLite 数据库连接
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # 路由汇总
│   │   │   ├── meetings.py     # 会议相关接口
│   │   │   └── participants.py # 参与者相关接口
│   ├── models/
│   │   ├── __init__.py
│   │   ├── meeting.py          # Meeting 模型
│   │   ├── participant.py      # Participant 模型
│   │   └── summary.py          # Summary 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── meeting.py          # Pydantic 请求/响应模型
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audio.py            # 音频处理服务
│   │   ├── separation.py       # 人声分离服务
│   │   └── llm.py              # 智谱GLM调用
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── processor.py        # 后台任务处理
│   └── utils/
│       ├── __init__.py
│       └── file.py             # 文件处理工具
├── uploads/                    # 上传文件存储
├── tests/                      # 测试目录
├── requirements.txt
├── .env.example
└── README.md
```

### 前端 (meeting-assistant-frontend)

```
meeting-assistant-frontend/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts            # 路由配置
│   ├── views/
│   │   ├── UploadView.vue      # 上传页
│   │   ├── MeetingListView.vue # 列表页
│   │   └── MeetingDetailView.vue # 详情页
│   ├── components/
│   │   ├── AudioUploader.vue
│   │   ├── MeetingCard.vue
│   │   ├── ParticipantList.vue
│   │   ├── SummaryViewer.vue
│   │   └── StatusBadge.vue
│   ├── api/
│   │   └── meeting.ts          # API 调用封装
│   ├── stores/
│   │   └── meeting.ts          # Pinia 状态管理
│   ├── types/
│   │   └── index.ts            # TypeScript 类型定义
│   └── styles/
│       └── main.css
├── package.json
├── vite.config.ts
├── tsconfig.json
└── README.md
```

## 错误处理

### 错误响应格式

```json
{
  "error": {
    "code": "AUDIO_FORMAT_NOT_SUPPORTED",
    "message": "不支持的音频格式，请上传 mp3/wav/m4a 文件"
  }
}
```

### 边界情况处理

| 场景 | 处理方式 |
|------|---------|
| 音频文件过大 | 前端限制100MB，后端校验，超限返回 413 |
| 不支持的格式 | 返回 400，提示支持的格式列表 |
| 人声分离API失败 | 任务标记为 failed，存储错误信息 |
| 大模型调用超时 | 重试3次，仍失败则标记 failed |
| 文件上传中断 | 清理临时文件，返回上传失败 |
| 删除处理中的会议 | 允许删除，中止后台任务 |
| 并发轮询过多 | 限流保护，建议轮询间隔3秒 |

### 前端错误提示

- 使用 Toast 提示临时错误（网络超时等）
- 使用 Modal 提示重要错误（处理失败等）
- 上传进度条显示上传状态

## 实施计划

### 阶段1：后端骨架搭建

- 使用 `fastapi-templates` skill 生成项目骨架
- 配置 SQLite 数据库连接
- 创建数据模型 (Meeting, Participant, Summary)

### 阶段2：API 开发

- 使用 `api-design-principles` skill 确保 API 规范
- 实现会议 CRUD 接口
- 实现文件上传接口
- 实现参与者名称修改接口
- 实现任务状态查询接口

### 阶段3：后台任务集成

- 集成人声分离第三方 API
- 集成智谱 GLM API
- 实现后台任务处理流程

### 阶段4：前端开发

- 使用 `frontend-design` skill 实现高质量 UI
- 上传页面开发
- 会议列表页开发
- 会议详情页开发（讯飞风格左右布局）

### 阶段5：测试

- 使用 `test` skill 生成测试用例
- 后端 API 测试
- 前端组件测试

### 阶段6：文档

- 使用 `docs-writer` skill 生成项目文档
- API 文档
- 部署文档

## Skill 使用清单

| Skill | 用途 |
|-------|------|
| fastapi-templates | 后端项目骨架搭建 |
| api-design-principles | API 设计规范检查 |
| frontend-design | 前端 UI 实现 |
| test | 测试用例生成 |
| docs-writer | 项目文档生成 |
