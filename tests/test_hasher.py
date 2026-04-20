import hashlib

from app.services.hasher import calculate_file_hash


def test_calculate_file_hash_returns_expected_sha256(tmp_path):
    file_path = tmp_path / "sample.txt"
    content = b"hello backup manager"
    file_path.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()

    actual_hash = calculate_file_hash(file_path)

    assert actual_hash == expected_hash