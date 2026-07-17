from pathlib import Path

import pytest

from file_organizer.classifiers import ONE_MIB, Rule
from file_organizer.exceptions import ClassificationError, InvalidDirectoryError
from file_organizer.organizer import (
    ConflictStrategy,
    MovePlan,
    move_files,
    organize,
    plan_moves,
    scan_files,
)


def test_scan_files_skips_hidden_files_and_directories(tmp_path: Path) -> None:
    visible = tmp_path / "visible.txt"
    visible.write_text("visible", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("hidden", encoding="utf-8")
    destination = tmp_path / "Documents"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")

    assert scan_files(tmp_path) == [visible]


def test_scan_files_skips_symbolic_links(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("content", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links are not available on this platform")

    assert scan_files(tmp_path) == [target]


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


def test_empty_directory_has_empty_result(tmp_path: Path) -> None:
    result = organize(tmp_path)

    assert result.planned == 0
    assert result.moved == 0
    assert result.skipped == 0
    assert result.failed == 0


def test_organize_moves_file_by_type(tmp_path: Path) -> None:
    source = tmp_path / "photo.jpg"
    source.write_bytes(b"image")

    result = organize(tmp_path)

    assert not source.exists()
    assert (tmp_path / "Images" / "photo.jpg").read_bytes() == b"image"
    assert result.moved == 1
    assert result.failed == 0


def test_organize_moves_unicode_filename(tmp_path: Path) -> None:
    source = tmp_path / "旅行计划.txt"
    source.write_text("content", encoding="utf-8")

    result = organize(tmp_path)

    assert (tmp_path / "Documents" / source.name).read_text(encoding="utf-8") == "content"
    assert result.moved == 1


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


def test_case_only_conflict_is_skipped(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("new", encoding="utf-8")
    destination_dir = tmp_path / "Documents"
    destination_dir.mkdir()
    existing = destination_dir / "REPORT.TXT"
    existing.write_text("existing", encoding="utf-8")

    result = organize(tmp_path)

    assert source.exists()
    assert existing.read_text(encoding="utf-8") == "existing"
    assert result.skipped == 1


def test_invalid_conflict_strategy_is_rejected_for_empty_plan() -> None:
    with pytest.raises(ValueError, match="Unsupported conflict strategy"):
        plan_moves([], Rule.TYPE, "overwrite")


def test_invalid_conflict_strategy_is_rejected_during_execution() -> None:
    with pytest.raises(ValueError, match="Unsupported conflict strategy"):
        move_files([], conflict_strategy="overwrite")


def test_invalid_rule_is_rejected_for_empty_plan() -> None:
    with pytest.raises(ValueError, match="Unsupported organization rule"):
        plan_moves([], "unknown", ConflictStrategy.SKIP)


def test_move_failure_is_reported_without_losing_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "report.txt"
    source.write_text("content", encoding="utf-8")
    plan = MovePlan(source, tmp_path / "Documents" / source.name)

    def fail_move(source_path: str, destination_path: str) -> None:
        raise PermissionError("move denied")

    monkeypatch.setattr("file_organizer.organizer.shutil.move", fail_move)
    errors: list[str] = []
    result = move_files([plan], output=lambda message: None, error_output=errors.append)

    assert source.exists()
    assert result.failed == 1
    assert result.moved == 0
    assert errors == ["ERROR    report.txt: move denied"]


def test_deleted_file_during_classification_raises_clear_error(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("content", encoding="utf-8")
    files = scan_files(tmp_path)
    source.unlink()

    with pytest.raises(ClassificationError, match="Could not classify"):
        plan_moves(files, Rule.SIZE)


def test_classification_uses_latest_file_metadata(tmp_path: Path) -> None:
    source = tmp_path / "report.bin"
    source.write_bytes(b"")
    files = scan_files(tmp_path)
    with source.open("r+b") as file:
        file.truncate(ONE_MIB)

    plans = plan_moves(files, Rule.SIZE)

    assert plans[0].destination.parent.name == "Medium (1-10MiB)"


def test_same_file_object_is_always_skipped(tmp_path: Path) -> None:
    source = tmp_path / "report.txt"
    source.write_text("content", encoding="utf-8")
    destination = tmp_path / "Documents" / source.name
    destination.parent.mkdir()
    try:
        destination.hardlink_to(source)
    except OSError:
        pytest.skip("hard links are not available on this platform")

    result = organize(tmp_path, conflict_strategy=ConflictStrategy.RENAME)

    assert source.exists()
    assert destination.exists()
    assert result.skipped == 1
    assert result.moved == 0
    assert not (destination.parent / "report (1).txt").exists()


def test_invalid_directory_has_clear_error(tmp_path: Path) -> None:
    with pytest.raises(InvalidDirectoryError, match="Directory does not exist"):
        organize(tmp_path / "missing")
