"""Add real-time transcription fields to meetings table."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def upgrade():
    """Add real-time fields to meetings table."""
    async with engine.begin() as conn:
        # Check if mode column exists
        result = await conn.execute(text("PRAGMA table_info(meetings)"))
        columns = [row[1] for row in result.fetchall()]

        # Add mode column (without NOT NULL constraint for existing data)
        if 'mode' not in columns:
            print("Adding mode column...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN mode VARCHAR(20) DEFAULT 'file_upload'"
            ))

        # Add other columns
        if 'websocket_id' not in columns:
            print("Adding websocket_id column...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN websocket_id VARCHAR(100)"
            ))

        if 'started_at' not in columns:
            print("Adding started_at column...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN started_at TIMESTAMP"
            ))

        if 'ended_at' not in columns:
            print("Adding ended_at column...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN ended_at TIMESTAMP"
            ))

        # Update any NULL mode values
        result = await conn.execute(text(
            "UPDATE meetings SET mode = 'file_upload' WHERE mode IS NULL"
        ))
        if result.rowcount > 0:
            print(f"Updated {result.rowcount} meetings with default mode")

    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(upgrade())
