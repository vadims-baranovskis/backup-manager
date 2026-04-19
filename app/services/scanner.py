import os
from datetime import datetime
from pathlib import Path

from app.models.file_record import FileRecord
from app.services.hasher import calculate_file_hash
from app.settings import get_scan_config


def format_scan_error(item, error):
    winerror = getattr(error, "winerror", None)

    if isinstance(error, FileNotFoundError) or winerror == 3:
        message = "File was not found during scanning."
    elif isinstance(error, PermissionError) or winerror == 5:
        message = "Access was denied during scanning."
    elif winerror == 206:
        message = "The file path is too long."
    else:
        message = f"Scan failed: {error.__class__.__name__}."

    return f"{item}: {message}"


def normalize_extensions(extensions):
    normalized = set()

    for extension in extensions:
        cleaned = extension.strip().casefold()
        if not cleaned:
            continue

        if not cleaned.startswith("."):
            cleaned = "." + cleaned

        normalized.add(cleaned)

    return normalized


def scan_directory(root_path):
    root = Path(root_path).expanduser().resolve()

    if not root.exists():
        raise ValueError("The specified folder does not exist.")

    if not root.is_dir():
        raise ValueError("The specified path is not a folder.")

    scan_config = get_scan_config()

    excluded_directories = {
        name.casefold() for name in scan_config["excluded_directories"]
    }
    excluded_extensions = normalize_extensions(
        scan_config["excluded_extensions"]
    )
    excluded_file_names = {
        name.casefold() for name in scan_config["excluded_file_names"]
    }

    records = []
    errors = []

    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            [
                directory_name
                for directory_name in dirnames
                if directory_name.casefold() not in excluded_directories
            ],
            key=str.casefold
        )

        current_root_path = Path(current_root)

        for file_name in sorted(filenames, key=str.casefold):
            if file_name.casefold() in excluded_file_names:
                continue

            file_suffixes = [suffix.casefold() for suffix in Path(file_name).suffixes]
            if any(suffix in excluded_extensions for suffix in file_suffixes):
                continue

            item = current_root_path / file_name

            try:
                if not item.is_file():
                    continue

                stat = item.stat()
                file_hash = calculate_file_hash(item)

                record = FileRecord(
                    path=str(item.resolve()),
                    name=item.name,
                    size=stat.st_size,
                    modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                    file_hash=file_hash
                )
                records.append(record)

            except (PermissionError, FileNotFoundError, OSError) as error:
                errors.append(format_scan_error(item, error))

    return records, errors