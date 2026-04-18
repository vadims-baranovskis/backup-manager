from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
BACKUPS_DIR = BASE_DIR / "backups"
DB_PATH = DATA_DIR / "backup_manager.db"
HASH_CHUNK_SIZE = 1024 * 1024  # 1 MB


def ensure_project_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    BACKUPS_DIR.mkdir(exist_ok=True)