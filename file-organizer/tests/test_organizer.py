from pathlib import Path

import pytest

from file_organizer.exceptions import InvalidDirectoryError
from file_organizer.organizer import organize, scan_files


def test_scan_files_skips_hidden_files_and_directories(tmp_path: Path) -> None:
    visible = tmp_path / "visible.txt"
    visible.write_text("visible", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")
    destination = tmp_path / "Documents"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")

    assert scan_files(tmp_path) == [visible]


def test_dry_run_does_not_change_filesystem(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("report", encoding="utf-8")
    messages: list[str] = []

    result = organize(tmp_path, dry_run=True, output=messages.append)

    assert source.exists()
    assert not (tmp_path / "Documents").exists()
    assert result.planned == 1
    assert result.moved == 0
    assert messages[0].startswith("WOULD MOVE")


def test_organize_moves_file_by_type(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    source.write_bytes(b"image")

    result = organize(tmp_path)

    assert not source.exists()
    assert (tmp_path / "Images" / "photo.jpg").read_bytes() == b"image"
    assert result.moved == 1
    assert result.failed == 0


def test_default_conflict_strategy_skips_without_overwriting(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("new", encoding="utf-8")
    destination = tmp_path / "Documents" / "report.txt"
    destination.parent.mkdir()
    destination.write_text("existing", encoding="utf-8")

    result = organize(tmp_path)

    assert source.read_text(encoding="utf-8") == "new"
    assert destination.read_text(encoding="utf-8") == "existing"
    assert result.skipped == 1
    assert result.moved == 0


def test_rename_conflict_strategy_preserves_both_files(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("new", encoding="utf-8")
    destination_dir = tmp_path / "Documents"
    destination_dir.mkdir()
    (destination_dir / "report.txt").write_text("existing", encoding="utf-8")
    (destination_dir / "report (1).txt").write_text("older", encoding="utf-8")

    result = organize(tmp_path, conflict_strategy="rename")

    assert (destination_dir / "report.txt").read_text(encoding="utf-8") == "existing"
    assert (destination_dir / "report (2).txt").read_text(encoding="utf-8") == "new"
    assert result.moved == 1


def test_invalid_directory_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(InvalidDirectoryError, match="Directory does not exist"):
        organize(tmp_path / "missing")
