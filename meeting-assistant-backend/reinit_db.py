"""重新初始化数据库脚本"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, engine
from sqlalchemy import text


async def drop_all_tables():
    """删除所有表"""
    async with engine.begin() as conn:
        # Get all table names
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table'
        """))
        tables = [row[0] for row in result.fetchall()]

        # Drop all tables
        for table in tables:
            if table != 'sqlite_sequence':
                await conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
                print(f"Dropped table: {table}")

        await conn.commit()
        print("All tables dropped!")


async def main():
    """主函数"""
    print("="*50)
    print("重新初始化数据库")
    print("="*50)
    print()

    # 1. 删除所有表
    print("步骤 1/3: 删除所有现有表...")
    await drop_all_tables()
    print()

    # 2. 运行迁移
    print("步骤 2/3: 运行数据库迁移...")
    from migrations.add_user_department import upgrade
    await upgrade()
    print()

    # 3. 初始化表结构（SQLAlchemy）
    print("步骤 3/3: 初始化 SQLAlchemy 表结构...")
    await init_db()
    print()

    print("="*50)
    print("数据库重新初始化完成！")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
