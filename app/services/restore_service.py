import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RestoreResult:
    success: bool
    message: str
    source_path: str
    backup_path: str
    restored_to: str


def restore_from_history_entry(history_entry, output_path=None, overwrite=False):
    source_path = history_entry["source_path"]
    backup_path = Path(history_entry["backup_path"])

    if output_path:
        requested_output = Path(output_path).expanduser()

        if requested_output.exists() and requested_output.is_dir():
            target_path = requested_output / Path(source_path).name
        else:
            target_path = requested_output
    else:
        target_path = Path(source_path)

    try:
        if not backup_path.exists():
            raise FileNotFoundError

        if target_path.exists() and not overwrite:
            raise FileExistsError

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, target_path)

        return RestoreResult(
            success=True,
            message="File was restored successfully.",
            source_path=source_path,
            backup_path=str(backup_path),
            restored_to=str(target_path)
        )

    except FileExistsError:
        return RestoreResult(
            success=False,
            message="Target file already exists. Use --overwrite to replace it.",
            source_path=source_path,
            backup_path=str(backup_path),
            restored_to=str(target_path)
        )

    except PermissionError:
        return RestoreResult(
            success=False,
            message="Access was denied during restore.",
            source_path=source_path,
            backup_path=str(backup_path),
            restored_to=str(target_path)
        )

    except FileNotFoundError:
        return RestoreResult(
            success=False,
            message="Backup file was not found.",
            source_path=source_path,
            backup_path=str(backup_path),
            restored_to=str(target_path)
        )

    except OSError as error:
        return RestoreResult(
            success=False,
            message=f"Restore failed: {error.__class__.__name__}.",
            source_path=source_path,
            backup_path=str(backup_path),
            restored_to=str(target_path)
        )