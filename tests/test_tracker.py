from app.models.file_record import FileRecord
from app.services.tracker import compare_states


def test_compare_states_detects_new_changed_unchanged_and_deleted_files():
    previous_files = {
        "C:\\test\\a.txt": {
            "path": "C:\\test\\a.txt",
            "name": "a.txt",
            "size": 10,
            "modified_at": "2026-04-18T10:00:00",
            "file_hash": "hash_a_old"
        },
        "C:\\test\\b.txt": {
            "path": "C:\\test\\b.txt",
            "name": "b.txt",
            "size": 20,
            "modified_at": "2026-04-18T10:00:00",
            "file_hash": "hash_b"
        },
        "C:\\test\\deleted.txt": {
            "path": "C:\\test\\deleted.txt",
            "name": "deleted.txt",
            "size": 30,
            "modified_at": "2026-04-18T10:00:00",
            "file_hash": "hash_deleted"
        }
    }

    current_records = [
        FileRecord(
            path="C:\\test\\a.txt",
            name="a.txt",
            size=11,
            modified_at="2026-04-18T11:00:00",
            file_hash="hash_a_new"
        ),
        FileRecord(
            path="C:\\test\\b.txt",
            name="b.txt",
            size=20,
            modified_at="2026-04-18T10:00:00",
            file_hash="hash_b"
        ),
        FileRecord(
            path="C:\\test\\new.txt",
            name="new.txt",
            size=15,
            modified_at="2026-04-18T11:00:00",
            file_hash="hash_new"
        )
    ]

    summary = compare_states(previous_files, current_records)

    assert summary.new_files == ["C:\\test\\new.txt"]
    assert summary.changed_files == ["C:\\test\\a.txt"]
    assert summary.unchanged_files == ["C:\\test\\b.txt"]
    assert summary.deleted_files == ["C:\\test\\deleted.txt"]