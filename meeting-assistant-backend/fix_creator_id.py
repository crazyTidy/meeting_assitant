"""快速修复：添加 creator_id 列到 meetings 表"""
import asyncio
import sqlite3


def fix_creator_id_column():
    """直接使用 sqlite3 添加 creator_id 列"""
    db_path = "meeting_assistant.db"

    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查列是否存在
    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]

    print(f"Current columns in meetings table: {columns}")

    if 'creator_id' in columns:
        print("OK: creator_id column already exists")
    else:
        print("Adding creator_id column...")
        try:
            cursor.execute("ALTER TABLE meetings ADD COLUMN creator_id VARCHAR(100)")
            conn.commit()
            print("OK: creator_id column added successfully")
        except Exception as e:
            print(f"ERROR: Failed to add column: {e}")

    # 再次检查
    cursor.execute("PRAGMA table_info(meetings)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Updated columns: {columns}")

    conn.close()


def ensure_users_table():
    """确保 users 表存在"""
    db_path = "meeting_assistant.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查 users 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if cursor.fetchone() is None:
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE users (
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
        """)

        # 插入测试用户
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, real_name)
            VALUES ('dev-user-001', 'dev_user', '开发测试用户')
        """)

        conn.commit()
        print("OK: users table created successfully")
    else:
        print("OK: users table already exists")

    conn.close()


if __name__ == "__main__":
    print("="*50)
    print("Fix Database: Add creator_id column")
    print("="*50)
    print()

    ensure_users_table()
    print()
    fix_creator_id_column()

    print()
    print("="*50)
    print("Fix completed! Please restart backend server")
    print("="*50)
