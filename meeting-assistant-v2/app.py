#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: system
Time: 2026/03/04
"""
"""Meeting Assistant Application - FastAPI Entry Point."""
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .models.database import init_db
from .routers import meeting_router, swagger_router
from .settings import directory_config, environment_config
from .utils import log_util


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    log_util.set_log(debug=True)
    logging.info("Starting Meeting Assistant application...")

    # Initialize database
    await init_db()

    # Create upload directory
    import os
    upload_dir = environment_config.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    logging.info(f"Upload directory ready: {upload_dir}")

    yield

    # Shutdown
    logging.info("Shutting down Meeting Assistant application...")


app = FastAPI(
    title="Meeting Assistant API",
    description="会议助手后端 API - 音频处理、人声分离、AI 纪要生成",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ==============================================================================
# 中间件配置
# ==============================================================================
# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头
    allow_credentials=True,  # 允许发送凭据
)

# ==============================================================================
# 挂载静态文件目录
# ==============================================================================
app.mount(
    "/statics",
    StaticFiles(directory=directory_config.CONST_STATIC_DIRECTORY),
    name="statics",
)

# ==============================================================================
# 路由注册
# ==============================================================================
# swagger 调试 router，不要删除
app.include_router(swagger_router.router)
# 会议相关路由
app.include_router(meeting_router.router)


# ==============================================================================
# 异常处理
# ==============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exception: Exception):
    """全局异常处理。"""
    logging.error(f"Global exception: {exception}", exc_info=True)
    body_json = {
        "code": 500,
        "message": "服务器出错，请重新请求。",
        "detail": str(exception) if environment_config.RELOAD else None
    }
    return JSONResponse(content=body_json, status_code=500)


# ==============================================================================
# 健康检查
# ==============================================================================
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "meeting-assistant-v2"
    }


# ==============================================================================
# 启动入口
# ==============================================================================
def run_as_http_server():
    """以 http 启动服务。"""
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
    )


def run_as_https_server():
    """以 https 单向认证启动服务。"""
    from .settings import file_config
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
        ssl_keyfile=file_config.CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=file_config.CONST_SERVER_CERTIFICATE,
    )


def run_as_https_server_client():
    """以 https 双向认证启动服务。"""
    from .settings import file_config
    uvicorn.run(
        app=f"{__package__}.app:app",
        host=environment_config.HOST,
        port=environment_config.PORT,
        reload=environment_config.RELOAD,
        workers=environment_config.WORKERS,
        ssl_keyfile=file_config.CONST_SERVER_PRIVATE_KEY,
        ssl_certfile=file_config.CONST_SERVER_CERTIFICATE,
        ssl_ca_certs=file_config.CONST_CA_CERTIFICATE,
        ssl_cert_reqs=2,
    )


def main():
    """启动入口。"""
    if environment_config.HTTPS == 0:
        run_as_http_server()
    elif environment_config.HTTPS == 1:
        run_as_https_server()
    elif environment_config.HTTPS == 2:
        run_as_https_server_client()
    else:
        raise Exception(f"wrong HTTPS value {environment_config.HTTPS}")


if __name__ == "__main__":
    main()
