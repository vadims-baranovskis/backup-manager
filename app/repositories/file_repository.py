from pathlib import Path


def normalize_path_for_compare(path):
    return str(Path(path).expanduser()).strip().replace("/", "\\").casefold()


class FileRepository:
    def __init__(self, connection):
        self.connection = connection

    def get_active_files_map(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT path, name, size, modified_at, file_hash
            FROM tracked_files
            WHERE status = 'active'
        """)
        rows = cursor.fetchall()

        result = {}
        for row in rows:
            result[row["path"]] = {
                "path": row["path"],
                "name": row["name"],
                "size": row["size"],
                "modified_at": row["modified_at"],
                "file_hash": row["file_hash"]
            }

        return result

    def upsert_file(self, file_record, scan_time):
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO tracked_files (
                path, name, size, modified_at, file_hash,
                status, first_seen_at, last_seen_at, deleted_at
            )
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, NULL)
            ON CONFLICT(path) DO UPDATE SET
                name = excluded.name,
                size = excluded.size,
                modified_at = excluded.modified_at,
                file_hash = excluded.file_hash,
                status = 'active',
                last_seen_at = excluded.last_seen_at,
                deleted_at = NULL
        """, (
            file_record.path,
            file_record.name,
            file_record.size,
            file_record.modified_at,
            file_record.file_hash,
            scan_time,
            scan_time
        ))

    def mark_files_deleted(self, deleted_paths, deleted_time):
        if not deleted_paths:
            return

        cursor = self.connection.cursor()
        cursor.executemany("""
            UPDATE tracked_files
            SET status = 'deleted',
                deleted_at = ?,
                last_seen_at = ?
            WHERE path = ?
        """, [(deleted_time, deleted_time, path) for path in deleted_paths])

    def add_history_entry(self, source_path, backup_path, file_hash, action, created_at):
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO backup_history (
                source_path,
                backup_path,
                file_hash,
                action,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            source_path,
            backup_path,
            file_hash,
            action,
            created_at
        ))

    def get_history(self, limit=20, path_query=None):
        cursor = self.connection.cursor()

        if path_query:
            cursor.execute("""
                SELECT source_path, backup_path, file_hash, action, created_at
                FROM backup_history
                WHERE source_path LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{path_query}%", limit))
        else:
            cursor.execute("""
                SELECT source_path, backup_path, file_hash, action, created_at
                FROM backup_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        return cursor.fetchall()

    def get_latest_restorable_entry(self, source_path):
        target_path = normalize_path_for_compare(source_path)

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT source_path, backup_path, file_hash, action, created_at
            FROM backup_history
            WHERE backup_path IS NOT NULL
              AND backup_path != ''
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()

        for row in rows:
            stored_path = normalize_path_for_compare(row["source_path"])
            if stored_path == target_path:
                return row

        return None

    def commit(self):
        self.connection.commit()