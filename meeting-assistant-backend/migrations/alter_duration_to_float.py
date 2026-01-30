"""Migration script to change duration column from INTEGER to FLOAT."""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "meeting_assistant.db"

def migrate():
    """Change duration column from INTEGER to FLOAT."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Begin transaction
        cur.execute("BEGIN TRANSACTION")

        # 1. Create new table with FLOAT duration (matching actual column order)
        cur.execute("""
            CREATE TABLE meetings_new (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                audio_path VARCHAR(512) NOT NULL,
                status VARCHAR(10) NOT NULL,
                progress INTEGER,
                error_message TEXT,
                duration FLOAT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                stage VARCHAR(50)
            )
        """)

        # 2. Copy data from old table to new table
        cur.execute("""
            INSERT INTO meetings_new (id, title, audio_path, status, progress, error_message, duration, created_at, updated_at, stage)
            SELECT id, title, audio_path, status, progress, error_message, duration, created_at, updated_at, stage FROM meetings
        """)

        # 3. Drop old table
        cur.execute("DROP TABLE meetings")

        # 4. Rename new table
        cur.execute("ALTER TABLE meetings_new RENAME TO meetings")

        # Commit transaction
        conn.commit()
        print("Migration successful: duration column changed to FLOAT")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
