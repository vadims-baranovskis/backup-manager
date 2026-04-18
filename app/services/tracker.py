from dataclasses import dataclass


@dataclass
class ScanSummary:
    new_files: list
    changed_files: list
    unchanged_files: list
    deleted_files: list


def compare_states(previous_files, current_records):
    current_map = {record.path: record for record in current_records}

    previous_paths = set(previous_files.keys())
    current_paths = set(current_map.keys())

    new_files = sorted(current_paths - previous_paths)
    deleted_files = sorted(previous_paths - current_paths)

    changed_files = []
    unchanged_files = []

    common_paths = sorted(previous_paths & current_paths)

    for path in common_paths:
        old_file = previous_files[path]
        new_file = current_map[path]

        if old_file["file_hash"] != new_file.file_hash:
            changed_files.append(path)
        else:
            unchanged_files.append(path)

    return ScanSummary(
        new_files=new_files,
        changed_files=changed_files,
        unchanged_files=unchanged_files,
        deleted_files=deleted_files
    )