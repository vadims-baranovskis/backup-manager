import hashlib
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from app.settings import BACKUPS_DIR


@dataclass
class BackupOperationResult:
    successful_paths: list
    errors: list


def sanitize_filename(name, max_length=50):
    cleaned = re.sub(r'[<>:"/\\|?*\s]+', "_", name).strip("._")
    if not cleaned:
        cleaned = "file"
    return cleaned[:max_length]


def build_backup_path(record, backup_run_folder):
    source = Path(record.path)

    suffix = "".join(source.suffixes)
    if len(suffix) > 20:
        suffix = source.suffix

    if suffix:
        stem = source.name[:-len(suffix)]
    else:
        stem = source.name

    safe_stem = sanitize_filename(stem)
    source_id = hashlib.sha1(record.path.encode("utf-8")).hexdigest()[:12]
    version_id = record.file_hash[:12]

    backup_file_name = f"{safe_stem}_{source_id}_{version_id}{suffix}"
    return BACKUPS_DIR / backup_run_folder / backup_file_name


def create_backups(records, action_map, scan_time, repository):
    backup_run_folder = scan_time.replace(":", "-").replace("T", "_")

    successful_paths = []
    errors = []

    run_folder = BACKUPS_DIR / backup_run_folder
    run_folder.mkdir(parents=True, exist_ok=True)

    for record in records:
        action = action_map.get(record.path, "updated")

        try:
            backup_path = build_backup_path(record, backup_run_folder)
            shutil.copy2(record.path, backup_path)

            repository.add_history_entry(
                source_path=record.path,
                backup_path=str(backup_path),
                file_hash=record.file_hash,
                action=action,
                created_at=scan_time
            )

            successful_paths.append(record.path)

        except (PermissionError, OSError, shutil.Error) as error:
            errors.append(f"{record.path}: {error}")

    return BackupOperationResult(
        successful_paths=successful_paths,
        errors=errors
    )