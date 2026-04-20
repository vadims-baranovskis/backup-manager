from app.services.restore_service import restore_from_history_entry


def test_restore_to_output_directory(tmp_path):
    backup_file = tmp_path / "backup_copy.txt"
    backup_file.write_text("restored content", encoding="utf-8")

    output_dir = tmp_path / "restore_here"
    output_dir.mkdir()

    original_source = tmp_path / "notes.txt"

    history_entry = {
        "source_path": str(original_source),
        "backup_path": str(backup_file)
    }

    result = restore_from_history_entry(
        history_entry=history_entry,
        output_path=str(output_dir)
    )

    restored_file = output_dir / "notes.txt"

    assert result.success is True
    assert restored_file.exists()
    assert restored_file.read_text(encoding="utf-8") == "restored content"


def test_restore_without_overwrite_returns_error_when_target_exists(tmp_path):
    backup_file = tmp_path / "backup_copy.txt"
    backup_file.write_text("new content", encoding="utf-8")

    target_file = tmp_path / "notes.txt"
    target_file.write_text("old content", encoding="utf-8")

    history_entry = {
        "source_path": str(target_file),
        "backup_path": str(backup_file)
    }

    result = restore_from_history_entry(history_entry=history_entry)

    assert result.success is False
    assert "already exists" in result.message.lower()
    assert target_file.read_text(encoding="utf-8") == "old content"