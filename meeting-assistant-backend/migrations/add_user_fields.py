"""Migration script to add user_id, user_name, department_id, department_name fields."""

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "meeting_assistant.db"


def migrate():
    """Add user isolation fields to meetings, participants, and summaries tables."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        # Begin transaction
        cur.execute("BEGIN TRANSACTION")

        # 1. Add user fields to meetings table
        print("Adding user fields to meetings table...")

        # Check if columns already exist
        cur.execute("PRAGMA table_info(meetings)")
        columns = [col[1] for col in cur.fetchall()]

        if 'user_id' not in columns:
            # Create new table with user fields
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
                    stage VARCHAR(50),
                    user_id VARCHAR(100) NOT NULL,
                    user_name VARCHAR(100) NOT NULL,
                    department_id VARCHAR(100) NOT NULL,
                    department_name VARCHAR(100) NOT NULL
                )
            """)

            # Copy existing data (use default values for existing records)
            cur.execute("""
                INSERT INTO meetings_new (
                    id, title, audio_path, status, progress, error_message, duration,
                    created_at, updated_at, stage, user_id, user_name, department_id, department_name
                )
                SELECT
                    id, title, audio_path, status, progress, error_message, duration,
                    created_at, updated_at, stage,
                    'system', 'System User', 'system', 'System Department'
                FROM meetings
            """)

            # Drop old table and rename new table
            cur.execute("DROP TABLE meetings")
            cur.execute("ALTER TABLE meetings_new RENAME TO meetings")

            # Create indexes
            cur.execute("CREATE INDEX ix_meetings_user_id ON meetings(user_id)")
            cur.execute("CREATE INDEX ix_meetings_department_id ON meetings(department_id)")

            print("  - meetings table updated")
        else:
            print("  - meetings table already has user fields")

        # 2. Add user fields to participants table
        print("Adding user fields to participants table...")

        cur.execute("PRAGMA table_info(participants)")
        columns = [col[1] for col in cur.fetchall()]

        if 'user_id' not in columns:
            cur.execute("""
                CREATE TABLE participants_new (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    meeting_id VARCHAR(36) NOT NULL REFERENCES meetings(id),
                    speaker_id VARCHAR(50) NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    voice_segment_path VARCHAR(512),
                    user_id VARCHAR(100) NOT NULL,
                    user_name VARCHAR(100) NOT NULL,
                    department_id VARCHAR(100) NOT NULL,
                    department_name VARCHAR(100) NOT NULL,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)

            # Copy existing data with default values
            cur.execute("""
                INSERT INTO participants_new (
                    id, meeting_id, speaker_id, display_name, voice_segment_path,
                    user_id, user_name, department_id, department_name
                )
                SELECT
                    id, meeting_id, speaker_id, display_name, voice_segment_path,
                    'system', 'System User', 'system', 'System Department'
                FROM participants
            """)

            cur.execute("DROP TABLE participants")
            cur.execute("ALTER TABLE participants_new RENAME TO participants")

            # Create indexes
            cur.execute("CREATE INDEX ix_participants_user_id ON participants(user_id)")
            cur.execute("CREATE INDEX ix_participants_department_id ON participants(department_id)")

            print("  - participants table updated")
        else:
            print("  - participants table already has user fields")

        # 3. Add user fields to summaries table
        print("Adding user fields to summaries table...")

        cur.execute("PRAGMA table_info(summaries)")
        columns = [col[1] for col in cur.fetchall()]

        if 'user_id' not in columns:
            cur.execute("""
                CREATE TABLE summaries_new (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    meeting_id VARCHAR(36) NOT NULL UNIQUE REFERENCES meetings(id),
                    content TEXT NOT NULL,
                    raw_response TEXT,
                    generated_at DATETIME NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    user_name VARCHAR(100) NOT NULL,
                    department_id VARCHAR(100) NOT NULL,
                    department_name VARCHAR(100) NOT NULL,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)

            # Copy existing data with default values
            cur.execute("""
                INSERT INTO summaries_new (
                    id, meeting_id, content, raw_response, generated_at,
                    user_id, user_name, department_id, department_name
                )
                SELECT
                    id, meeting_id, content, raw_response, generated_at,
                    'system', 'System User', 'system', 'System Department'
                FROM summaries
            """)

            cur.execute("DROP TABLE summaries")
            cur.execute("ALTER TABLE summaries_new RENAME TO summaries")

            # Create indexes
            cur.execute("CREATE INDEX ix_summaries_user_id ON summaries(user_id)")
            cur.execute("CREATE INDEX ix_summaries_department_id ON summaries(department_id)")

            print("  - summaries table updated")
        else:
            print("  - summaries table already has user fields")

        # Commit transaction
        conn.commit()
        print("\nMigration successful: User isolation fields added to all tables")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
