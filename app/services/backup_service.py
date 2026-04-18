import shutil
from dataclasses import dataclass
from pathlib import Path

from app.settings import BACKUPS_DIR


@dataclass
class BackupOperationResult:
    successful_paths: list
    errors: list


def build_backup_path(source_path, backup_run_folder):
    source = Path(source_path)
    parts = list(source.parts)
    anchor = source.anchor

    if anchor and parts and parts[0] == anchor:
        parts = parts[1:]

    target = BACKUPS_DIR / backup_run_folder

    if anchor:
        clean_anchor = anchor.replace(":", "").replace("\\", "").replace("/", "")
        if clean_anchor:
            target = target / clean_anchor

    for part in parts:
        target = target / part

    return target


def create_backups(records, scan_time):
    backup_run_folder = scan_time.replace(":", "-").replace("T", "_")

    successful_paths = []
    errors = []

    for record in records:
        try:
            backup_path = build_backup_path(record.path, backup_run_folder)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(record.path, backup_path)
            successful_paths.append(record.path)

        except (PermissionError, OSError, shutil.Error) as error:
            errors.append(f"{record.path}: {error}")

    return BackupOperationResult(
        successful_paths=successful_paths,
        errors=errors
    )