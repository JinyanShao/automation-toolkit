from datetime import datetime
from pathlib import Path

import pytest

from file_organizer.classifiers import (
    ONE_MIB,
    TEN_MIB,
    classify_by_size,
    classify_by_type,
    classify_by_year,
    classify_file,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("photo.JPG", "Images"),
        ("report.pdf", "Documents"),
        ("program.py", "Code"),
        ("README", "Others"),
    ],
)
def test_classify_by_type(filename: str, expected: str) -> None:
    assert classify_by_type(Path(filename)) == expected


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        (ONE_MIB - 1, "Small (<1MiB)"),
        (ONE_MIB, "Medium (1-10MiB)"),
        (TEN_MIB - 1, "Medium (1-10MiB)"),
        (TEN_MIB, "Large (>=10MiB)"),
    ],
)
def test_classify_by_size_boundaries(tmp_path: Path, size: int, expected: str) -> None:
    sample = tmp_path / "sample.bin"
    with sample.open("wb") as file:
        file.truncate(size)
    assert classify_by_size(sample) == expected


def test_classify_by_year_uses_modification_time(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("content", encoding="utf-8")
    timestamp = datetime(2020, 6, 1).timestamp()
    sample.touch()
    import os

    os.utime(sample, (timestamp, timestamp))
    assert classify_by_year(sample) == "2020"


def test_unknown_rule_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported organization rule"):
        classify_file(Path("sample.txt"), "unknown")
