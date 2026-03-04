"""Fix existing meetings mode values."""
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
        # Check if mode column exists
        result = await conn.execute(text("PRAGMA table_info(meetings)"))
        columns = [row[1] for row in result.fetchall()]

        if 'mode' not in columns:
            print("Adding mode column without NOT NULL constraint first...")
            await conn.execute(text(
                "ALTER TABLE meetings ADD COLUMN mode VARCHAR(20)"
            ))

        # Update all NULL or empty mode values to 'file_upload'
        result = await conn.execute(text(
            "UPDATE meetings SET mode = 'file_upload' WHERE mode IS NULL OR mode = ''"
        ))
        updated_count = result.rowcount
        print(f"Updated {updated_count} meetings with mode='file_upload'")

        # Now make the column NOT NULL (SQLite requires recreating table)
        print("Making mode column NOT NULL...")

        # Get current data
        result = await conn.execute(text("SELECT * FROM meetings"))
        meetings_data = result.fetchall()
        columns_info = await conn.execute(text("PRAGMA table_info(meetings)"))
        column_names = [row[1] for row in columns_info.fetchall()]

        # Create new table with correct schema
        columns_def = []
        for col_name in column_names:
            col_info = await conn.execute(text(f"PRAGMA table_info(meetings) AND name='{col_name}'"))
            info = col_info.fetchone()
            if info:
                col_type = info[2]  # type
                not_null = info[3]   # notnull
                default_val = info[4]  # dflt_value

                col_def = f"{col_name} {col_type}"
                if col_name == 'mode':
                    col_def += " NOT NULL DEFAULT 'file_upload'"
                elif not_null:
                    col_def += " NOT NULL"
                if default_val:
                    col_def += f" DEFAULT {default_val}"

                columns_def.append(col_def)

        create_sql = f"CREATE TABLE meetings_new ({', '.join(columns_def)})"
        await conn.execute(text(create_sql))

        # Copy data
        if meetings_data:
            placeholders = ', '.join(['?' for _ in column_names])
            columns_str = ', '.join(column_names)

            for row in meetings_data:
                insert_sql = f"INSERT INTO meetings_new ({columns_str}) VALUES ({placeholders})"
                await conn.execute(text(insert_sql), list(row))

        # Drop old table and rename new one
        await conn.execute(text("DROP TABLE meetings"))
        await conn.execute(text("ALTER TABLE meetings_new RENAME TO meetings"))

        # Recreate indexes
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings(created_at)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_meetings_status ON meetings(status)"))

    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(upgrade())
