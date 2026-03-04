"""Create real_time_segments table."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def upgrade():
    """Create real_time_segments table."""
    async with engine.begin() as conn:
        # Check if table exists
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='real_time_segments'"
        ))
        table_exists = result.fetchone() is not None

        if not table_exists:
            print("Creating real_time_segments table...")
            await conn.execute(text("""
                CREATE TABLE real_time_segments (
                    id VARCHAR(36) PRIMARY KEY,
                    meeting_id VARCHAR(36) NOT NULL,
                    speaker_id VARCHAR(50) NOT NULL,
                    text TEXT NOT NULL,
                    start_time FLOAT NOT NULL,
                    end_time FLOAT NOT NULL,
                    is_final BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """))

            # Create index for faster queries
            print("Creating index...")
            await conn.execute(text(
                "CREATE INDEX idx_realtime_meeting ON real_time_segments(meeting_id)"
            ))

            print("real_time_segments table created successfully!")
        else:
            print("real_time_segments table already exists!")


if __name__ == "__main__":
    asyncio.run(upgrade())
