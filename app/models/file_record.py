from dataclasses import dataclass


@dataclass
class FileRecord:
    path: str
    name: str
    size: int
    modified_at: str
    file_hash: str