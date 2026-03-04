"""Fix existing meetings mode values - simplified version."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def upgrade():
    """Fix mode column for existing records."""
    async with engine.begin() as conn:
        # First, check current state
        result = await conn.execute(text("SELECT id, mode FROM meetings"))
        meetings = result.fetchall()
        print(f"Found {len(meetings)} meetings")

        for meeting in meetings:
            meeting_id, mode = meeting
            print(f"  Meeting {meeting_id}: mode={mode}")

        # Get all column names
        result = await conn.execute(text("PRAGMA table_info(meetings)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Columns: {columns}")

        # Check if mode column exists
        if 'mode' not in columns:
            print("Adding mode column...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN mode VARCHAR(20) DEFAULT 'file_upload'"
            ))

        # Update all records that have NULL or incorrect mode
        result = await conn.execute(text(
            "UPDATE meetings SET mode = 'file_upload' WHERE mode IS NULL OR mode != 'file_upload' OR mode != 'real_time'"
        ))
        print(f"Updated {result.rowcount} meetings")

        # Verify the update
        result = await conn.execute(text("SELECT id, mode FROM meetings"))
        meetings = result.fetchall()
        print("\nAfter update:")
        for meeting in meetings:
            meeting_id, mode = meeting
            print(f"  Meeting {meeting_id}: mode={mode}")

    print("\nMigration completed successfully!")


if __name__ == "__main__":
    asyncio.run(upgrade())
