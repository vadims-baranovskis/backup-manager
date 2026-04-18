from app.db.connection import get_connection


def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                size INTEGER NOT NULL,
                modified_at TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL,
                deleted_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backup_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                action TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracked_files_status
            ON tracked_files(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tracked_files_hash
            ON tracked_files(file_hash)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_backup_history_created_at
            ON backup_history(created_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_backup_history_source_path
            ON backup_history(source_path)
        """)

        connection.commit()