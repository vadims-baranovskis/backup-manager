import argparse

from app.db.schema import init_db
from app.settings import ensure_project_dirs


def handle_init():
    ensure_project_dirs()
    init_db()
    print("Project folders and database have been initialized.")


def run_cli():
    parser = argparse.ArgumentParser(
        description="Backup and File Indexing Manager"
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("init", help="Create project folders and database")

    args = parser.parse_args()

    if args.command == "init":
        handle_init()
    else:
        parser.print_help()