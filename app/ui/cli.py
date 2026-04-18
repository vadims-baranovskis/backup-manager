import argparse

from app.db.schema import init_db
from app.services.scanner import scan_directory
from app.settings import ensure_project_dirs


def print_scan_result(records, scan_errors):
    print("\n=== Scan Result ===")
    print(f"Files found: {len(records)}")
    print(f"Access errors: {len(scan_errors)}")

    if records:
        print("\nDetected files:")
        for record in records[:10]:
            print(f"  - {record.path}")

    if scan_errors:
        print("\nSkipped files due to errors:")
        for error in scan_errors[:10]:
            print(f"  ! {error}")


def handle_init():
    ensure_project_dirs()
    init_db()
    print("Project folders and database have been initialized.")


def handle_scan(scan_path):
    records, scan_errors = scan_directory(scan_path)
    print_scan_result(records, scan_errors)


def run_cli():
    parser = argparse.ArgumentParser(
        description="Backup and File Indexing Manager"
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init", help="Create project folders and database")

    scan_parser = subparsers.add_parser("scan", help="Scan a folder")
    scan_parser.add_argument(
        "--path",
        required=True,
        help="Path to the folder to scan"
    )

    args = parser.parse_args()

    if args.command == "init":
        handle_init()
    elif args.command == "scan":
        handle_scan(args.path)
    else:
        parser.print_help()