from app.services import scanner


def test_scan_directory_skips_excluded_items(tmp_path, monkeypatch):
    root = tmp_path / "scan_root"
    root.mkdir()

    (root / "visible.txt").write_text("visible", encoding="utf-8")
    (root / "notes.txt").write_text("notes", encoding="utf-8")
    (root / "Thumbs.db").write_text("ignored", encoding="utf-8")

    packages_dir = root / "packages"
    packages_dir.mkdir()
    (packages_dir / "hidden.txt").write_text("hidden", encoding="utf-8")

    node_modules_dir = root / "node_modules"
    node_modules_dir.mkdir()
    (node_modules_dir / "lib.js").write_text("console.log('x');", encoding="utf-8")

    logs_dir = root / "logs"
    logs_dir.mkdir()
    (logs_dir / "app.log").write_text("log content", encoding="utf-8")

    subfolder_dir = root / "subfolder"
    subfolder_dir.mkdir()
    (subfolder_dir / "todo.txt").write_text("task", encoding="utf-8")

    monkeypatch.setattr(
        scanner,
        "get_scan_config",
        lambda: {
            "excluded_directories": [
                "packages",
                "node_modules",
                "__pycache__"
            ],
            "excluded_extensions": [
                ".log",
                ".tmp",
                ".cache"
            ],
            "excluded_file_names": [
                "Thumbs.db"
            ]
        }
    )

    records, errors = scanner.scan_directory(root)

    found_names = sorted(record.name for record in records)

    assert errors == []
    assert found_names == ["notes.txt", "todo.txt", "visible.txt"]