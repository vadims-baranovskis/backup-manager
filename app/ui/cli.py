import argparse
from datetime import datetime

from app.db.connection import get_connection
from app.db.schema import init_db
from app.repositories.file_repository import FileRepository
from app.services.backup_service import create_backups
from app.services.scanner import scan_directory
from app.services.tracker import compare_states
from app.settings import ensure_project_dirs


def print_scan_summary(summary, scan_errors):
    print("\n=== Scan Result ===")
    print(f"New files: {len(summary.new_files)}")
    print(f"Changed files: {len(summary.changed_files)}")
    print(f"Unchanged files: {len(summary.unchanged_files)}")
    print(f"Deleted files: {len(summary.deleted_files)}")
    print(f"Access errors: {len(scan_errors)}")

    if summary.new_files:
        print("\nNew files:")
        for path in summary.new_files[:10]:
            print(f"  + {path}")

    if summary.changed_files:
        print("\nChanged files:")
        for path in summary.changed_files[:10]:
            print(f"  * {path}")

    if summary.deleted_files:
        print("\nDeleted files:")
        for path in summary.deleted_files[:10]:
            print(f"  - {path}")

    if scan_errors:
        print("\nSkipped files due to errors:")
        for error in scan_errors[:10]:
            print(f"  ! {error}")


def print_backup_summary(summary, backup_result, scan_errors):
    print("\n=== Backup Result ===")
    print(f"New files: {len(summary.new_files)}")
    print(f"Changed files: {len(summary.changed_files)}")
    print(f"Unchanged files: {len(summary.unchanged_files)}")
    print(f"Deleted files: {len(summary.deleted_files)}")
    print(f"Backed up successfully: {len(backup_result.successful_paths)}")
    print(f"Backup errors: {len(backup_result.errors)}")
    print(f"Scan access errors: {len(scan_errors)}")

    if summary.new_files:
        print("\nNew files:")
        for path in summary.new_files[:10]:
            print(f"  + {path}")

    if summary.changed_files:
        print("\nChanged files:")
        for path in summary.changed_files[:10]:
            print(f"  * {path}")

    if summary.deleted_files:
        print("\nDeleted files:")
        for path in summary.deleted_files[:10]:
            print(f"  - {path}")

    if backup_result.errors:
        print("\nBackup errors:")
        for error in backup_result.errors[:10]:
            print(f"  ! {error}")

    if scan_errors:
        print("\nSkipped files due to scan errors:")
        for error in scan_errors[:10]:
            print(f"  ! {error}")


def handle_init():
    ensure_project_dirs()
    init_db()
    print("Project folders and database have been initialized.")


def handle_scan(scan_path):
    ensure_project_dirs()
    init_db()

    current_records, scan_errors = scan_directory(scan_path)

    with get_connection() as connection:
        repository = FileRepository(connection)
        previous_files = repository.get_active_files_map()

    summary = compare_states(previous_files, current_records)

    print_scan_summary(summary, scan_errors)
    print("\nPreview only. No changes were written to the database.")


def handle_backup(scan_path):
    ensure_project_dirs()
    init_db()

    current_records, scan_errors = scan_directory(scan_path)
    scan_time = datetime.now().isoformat(timespec="seconds")
    current_map = {record.path: record for record in current_records}

    with get_connection() as connection:
        repository = FileRepository(connection)
        previous_files = repository.get_active_files_map()

        summary = compare_states(previous_files, current_records)

        records_to_backup = []
        for path in summary.new_files + summary.changed_files:
            records_to_backup.append(current_map[path])

        backup_result = create_backups(records_to_backup, scan_time)
        successful_backup_paths = set(backup_result.successful_paths)

        for path in summary.unchanged_files:
            repository.upsert_file(current_map[path], scan_time)

        for path in summary.new_files + summary.changed_files:
            if path in successful_backup_paths:
                repository.upsert_file(current_map[path], scan_time)

        repository.mark_files_deleted(summary.deleted_files, scan_time)
        repository.commit()

    print_backup_summary(summary, backup_result, scan_errors)


def run_cli():
    parser = argparse.ArgumentParser(
        description="Backup and File Indexing Manager"
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init", help="Create project folders and database")

    scan_parser = subparsers.add_parser("scan", help="Preview folder changes")
    scan_parser.add_argument(
        "--path",
        required=True,
        help="Path to the folder to scan"
    )

    backup_parser = subparsers.add_parser("backup", help="Create backups and update database")
    backup_parser.add_argument(
        "--path",
        required=True,
        help="Path to the folder to back up"
    )

    args = parser.parse_args()

    if args.command == "init":
        handle_init()
    elif args.command == "scan":
        handle_scan(args.path)
    elif args.command == "backup":
        handle_backup(args.path)
    else:
        parser.print_help()