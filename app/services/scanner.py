from datetime import datetime
from pathlib import Path

from app.models.file_record import FileRecord
from app.services.hasher import calculate_file_hash


def scan_directory(root_path):
    root = Path(root_path).resolve()

    if not root.exists():
        raise ValueError("The specified folder does not exist.")

    if not root.is_dir():
        raise ValueError("The specified path is not a folder.")

    records = []
    errors = []

    for item in root.rglob("*"):
        try:
            if not item.is_file():
                continue

            stat = item.stat()
            file_hash = calculate_file_hash(item)

            record = FileRecord(
                path=str(item),
                name=item.name,
                size=stat.st_size,
                modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                file_hash=file_hash
            )
            records.append(record)

        except (PermissionError, OSError) as error:
            errors.append(f"{item}: {error}")

    return records, errors