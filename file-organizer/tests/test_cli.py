from pathlib import Path

import pytest

from file_organizer import cli
from file_organizer.exceptions import InvalidDirectoryError


def test_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--help"])

    assert exc_info.value.code == 0
    assert "usage: file-organizer" in capsys.readouterr().out


def test_invalid_argument_exits_with_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main([str(tmp_path), "--rule", "invalid"])

    assert exc_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_invalid_directory_returns_application_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = cli.main([str(tmp_path / "missing")])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Directory does not exist" in captured.err
    assert "Directory does not exist" not in captured.out


def test_successful_execution_returns_zero(tmp_path: Path) -> None:
    assert cli.main([str(tmp_path), "--dry-run"]) == 0


def test_file_move_failure_returns_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "report.txt").write_text("content", encoding="utf-8")

    def fail_move(source: str, destination: str) -> None:
        raise PermissionError("move denied")

    monkeypatch.setattr("file_organizer.organizer.shutil.move", fail_move)

    assert cli.main([str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "move denied" in captured.err
    assert "move denied" not in captured.out


def test_application_error_returns_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_organize(*args: object, **kwargs: object) -> None:
        raise InvalidDirectoryError("application failure")

    monkeypatch.setattr(cli, "organize", fail_organize)

    assert cli.main([str(tmp_path)]) == 2
    captured = capsys.readouterr()
    assert "application failure" in captured.err
    assert "application failure" not in captured.out
