# Meeting Assistant - Docker 部署指南

## 一键启动

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

## 手动部署

### 1. 配置环境变量

编辑 `.env` 文件，填入你的API密钥：

```env
ZHIPU_API_KEY=your_zhipu_api_key_here
SEPARATION_API_KEY=your_separation_api_key_here
SEPARATION_API_URL=https://api.example.com/separation
```

### 2. 构建并启动

```bash
docker-compose up -d --build
```

### 3. 查看日志

```bash
docker-compose logs -f
```

### 4. 停止服务

```bash
docker-compose down
```

## 访问地址

- 前端: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 目录结构

```
.
├── docker-compose.yml          # Docker编排配置
├── .env                        # 环境变量配置
├── start.bat / start.sh        # 启动脚本
├── stop.bat / stop.sh          # 停止脚本
├── meeting-assistant-backend/
│   ├── Dockerfile              # 后端镜像构建
│   └── .dockerignore           # 后端构建排除
└── meeting-assistant-frontend/
    ├── Dockerfile              # 前端镜像构建
    ├── nginx.conf              # Nginx配置
    └── .dockerignore           # 前端构建排除
```

## 常见问题

### 端口冲突
如果80或8000端口被占用，修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "8080:80"    # 前端改用8080
  - "8001:8000"  # 后端改用8001
```

### 数据持久化
上传的文件和数据库存储在Docker卷中，删除容器不会丢失数据。

### 重新构建
代码修改后重新构建：
```bash
docker-compose up -d --build
```

### 清理所有数据
```bash
docker-compose down -v
```
