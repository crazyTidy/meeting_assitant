"""初始化数据库表（运行迁移）"""
import asyncio
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.core.database import init_db


async def main():
    """初始化数据库"""
    print("初始化数据库...")
    await init_db()
    print("数据库初始化完成！")


if __name__ == "__main__":
    asyncio.run(main())
