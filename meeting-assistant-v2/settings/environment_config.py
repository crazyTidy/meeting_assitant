#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Environment configuration for meeting assistant application."""
import os

# ==============================================================================
# 基础配置
# ==============================================================================
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
RELOAD = int(os.environ.get("RELOAD", "1"))
WORKERS = int(os.environ.get("WORKERS", "1"))

# 证书配置
# 0 表示使用 http
# 1 表示开启 https 单向认证
# 2 表示开启 https 双向认证
HTTPS = int(os.environ.get("HTTPS", "0"))

# ==============================================================================
# 数据库配置
# ==============================================================================
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL",
    "sqlite+aiosqlite:///./meeting_assistant.db"
)

# ==============================================================================
# 会议助手配置
# ==============================================================================
# 文件上传目录
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
# 最大上传大小 (100MB)
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", str(100 * 1024 * 1024)))
# 允许的音频格式
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

# ==============================================================================
# API 配置
# ==============================================================================
# 智谱 AI API Key (用于生成会议纪要)
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "")

# 人声分离 API 配置
SEPARATION_API_KEY = os.environ.get("SEPARATION_API_KEY", "")
SEPARATION_API_URL = os.environ.get(
    "SEPARATION_API_URL",
    "http://192.168.0.100:40901/recognize"
)

# ASR 语音转文字 API 配置
ASR_API_KEY = os.environ.get("ASR_API_KEY", "")
ASR_API_URL = os.environ.get("ASR_API_URL", "")

# ==============================================================================
# Redis 配置 (可选)
# ==============================================================================
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))

# ==============================================================================
# MinIO 配置 (可选)
# ==============================================================================
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "")

# ==============================================================================
# Session 配置 (可选)
# ==============================================================================
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "your-secret-key-here")
SESSION_TYPE = os.environ.get("SESSION_TYPE", "0")  # 0: cookie, 1: authorization, 2: redis

# ==============================================================================
# 用户服务配置
# ==============================================================================
# 用户服务接口地址
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:8001")

# 权限服务接口地址
PERMISSION_SERVICE_URL = os.environ.get("PERMISSION_SERVICE_URL", "http://localhost:8002")

# 部门服务接口地址
DEPARTMENT_SERVICE_URL = os.environ.get("DEPARTMENT_SERVICE_URL", "http://localhost:8003")

# 接口超时时间（秒）
USER_REQUEST_TIMEOUT = int(os.environ.get("USER_REQUEST_TIMEOUT", "30"))


def main():
    """Main function for testing."""
    print(f"HOST: {HOST}")
    print(f"PORT: {PORT}")
    print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"Upload Dir: {UPLOAD_DIR}")


if __name__ == "__main__":
    main()
