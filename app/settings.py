import json
from copy import deepcopy
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUPS_DIR = BASE_DIR / "backups"
DB_PATH = DATA_DIR / "backup_manager.db"
CONFIG_PATH = BASE_DIR / "config.json"
HASH_CHUNK_SIZE = 1024 * 1024  # 1 MB

DEFAULT_CONFIG = {
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


def ensure_project_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    BACKUPS_DIR.mkdir(exist_ok=True)
    ensure_config_file()


def ensure_config_file():
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)


def load_config():
    ensure_config_file()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            user_config = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("The configuration file is not valid JSON.") from error

    merged_config = deepcopy(DEFAULT_CONFIG)

    if not isinstance(user_config, dict):
        return merged_config

    user_scan_config = user_config.get("scan")
    if isinstance(user_scan_config, dict):
        for key in ("excluded_directories", "excluded_extensions", "excluded_file_names"):
            value = user_scan_config.get(key)
            if isinstance(value, list):
                merged_config["scan"][key] = value

    return merged_config


def normalize_string_list(values):
    normalized = []

    for value in values:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                normalized.append(cleaned)

    return normalized


def get_scan_config():
    config = load_config()
    scan_config = config.get("scan", {})

    return {
        "excluded_directories": normalize_string_list(
            scan_config.get("excluded_directories", [])
        ),
        "excluded_extensions": normalize_string_list(
            scan_config.get("excluded_extensions", [])
        ),
        "excluded_file_names": normalize_string_list(
            scan_config.get("excluded_file_names", [])
        )
    }