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

    def commit(self):
        self.connection.commit()