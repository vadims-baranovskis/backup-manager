# Backup Manager

Backup Manager is a Python CLI application for file indexing, change detection, incremental backups, history tracking, and file restore.


## Features

- Initialize project folders and database
- Scan a folder and preview detected changes
- Detect:
  - new files
  - changed files
  - unchanged files
  - deleted files
- Create backup copies for new and changed files
- Store file state in SQLite
- Track backup history
- Restore the latest saved version of a file
- Exclude selected directories and files through `config.json`
- Run automated tests with `pytest`

## Project Structure

```text
backup_manager/
│
├── main.py
├── config.json
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
│
├── app/
│   ├── app.py
│   ├── settings.py
│   │
│   ├── db/
│   │   ├── connection.py
│   │   └── schema.py
│   │
│   ├── models/
│   │   └── file_record.py
│   │
│   ├── repositories/
│   │   └── file_repository.py
│   │
│   ├── services/
│   │   ├── backup_service.py
│   │   ├── hasher.py
│   │   ├── restore_service.py
│   │   ├── scanner.py
│   │   └── tracker.py
│   │
│   └── ui/
│       └── cli.py
│
├── data/
├── backups/
└── tests/
    ├── test_hasher.py
    ├── test_restore_service.py
    ├── test_scanner.py
    └── test_tracker.py
```

## Requirements

- Python 3.12 or newer

## Setup

Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install development dependencies.

```powershell
pip install -r requirements-dev.txt
```

## Commands

### Initialize project folders and database

```powershell
python main.py init
```

### Preview changes in a folder

```powershell
python main.py scan --path "C:\Path\To\Folder"
```

### Create backups and update the database

```powershell
python main.py backup --path "C:\Path\To\Folder"
```

### Show backup history

```powershell
python main.py history
```

Filter history by path fragment.

```powershell
python main.py history --path "notes.txt"
```

Limit the number of history entries.

```powershell
python main.py history --limit 10
```

### Restore the latest saved version of a file

Restore to the original location.

```powershell
python main.py restore --source-path "C:\Path\To\File.txt"
```

Restore to another folder.

```powershell
python main.py restore --source-path "C:\Path\To\File.txt" --output-path "C:\Path\To\RestoreFolder"
```

Overwrite the target file if it already exists.

```powershell
python main.py restore --source-path "C:\Path\To\File.txt" --overwrite
```

## Configuration

The project uses `config.json`.

Example:

```json
{
    "scan": {
        "excluded_directories": [
            "packages",
            "bin",
            "obj",
            ".git",
            "node_modules",
            "__pycache__",
            ".venv",
            ".pytest_cache"
        ],
        "excluded_extensions": [
            ".tmp",
            ".log",
            ".cache"
        ],
        "excluded_file_names": [
            "Thumbs.db",
            ".DS_Store"
        ]
    }
}
```

These settings allow the scanner to ignore unnecessary directories and files during scan and backup operations.

## Running Tests

```powershell
python -m pytest -q
```

## What This Project Demonstrates

- Python CLI application structure
- File system traversal
- SHA-256 hashing
- SQLite database integration
- Change tracking logic
- Backup and restore workflow
- JSON configuration support
- Automated testing with pytest

## Possible Future Improvements

- Restore a selected historical version, not only the latest one
- Export history to CSV
- Add logging to file
- Add a richer terminal UI
- Add more detailed backup statistics