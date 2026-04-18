import sqlite3

from app.settings import DB_PATH, ensure_project_dirs


def get_connection():
    ensure_project_dirs()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection