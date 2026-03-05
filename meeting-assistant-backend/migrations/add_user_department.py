"""Database migration: Add user table and modify meetings table.

This migration adds:
1. users table (stores external user info)
2. creator_id column to meetings table
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine


async def upgrade():
    """Add user table and modify meetings table."""
    async with engine.begin() as conn:
        # Create users table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(100) PRIMARY KEY,
                username VARCHAR(100),
                real_name VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                department_id VARCHAR(100),
                department_name VARCHAR(100),
                position VARCHAR(50),
                last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Check if meetings table exists and has creator_id column
        check_table = await conn.execute(text("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='meetings'
        """))
        meetings_exists = check_table.fetchone() is not None

        if meetings_exists:
            check_column = await conn.execute(text("""
                PRAGMA table_info(meetings)
            """))
            columns = [row[1] for row in check_column.fetchall()]

            if 'creator_id' not in columns:
                await conn.execute(text("""
                    ALTER TABLE meetings ADD COLUMN creator_id VARCHAR(100)
                """))
                print("Added creator_id column to meetings table")
            else:
                print("creator_id column already exists in meetings table")
        else:
            print("meetings table does not exist yet, will be created by SQLAlchemy")

        # Create default test user
        await conn.execute(text("""
            INSERT OR IGNORE INTO users (id, username, real_name)
            VALUES ('dev-user-001', 'dev_user', '开发测试用户')
        """))

        await conn.commit()
        print("Migration completed successfully!")


async def downgrade():
    """Remove user table and revert meetings table."""
    async with engine.begin() as conn:
        # Remove column from meetings
        try:
            await conn.execute(text("""
                ALTER TABLE meetings DROP COLUMN creator_id
            """))
            print("Dropped creator_id column from meetings table")
        except Exception:
            pass  # Column might not exist

        # Drop users table
        await conn.execute(text("DROP TABLE IF EXISTS users"))
        print("Dropped users table")

        await conn.commit()
        print("Rollback completed successfully!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
