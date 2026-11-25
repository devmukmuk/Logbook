"""Backstop for the pre-commit hook: hooks are local and can be skipped, so also check here."""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "tools" / "git-hooks" / "check-data-files.sh"
SH = shutil.which("sh")

pytestmark = pytest.mark.skipif(SH is None, reason="needs a POSIX sh (Git Bash)")


def run_checker(paths: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [SH, str(CHECKER)], input="\n".join(paths) + "\n", capture_output=True, text=True
    )


@pytest.mark.parametrize(
    "path",
    [
        "data/logbook.json",
        "Imports/foreflight.csv",
        "exports/summary.txt",
        "logs/2026-11-25.log",
        "my-hours.CSV",
        "notes/resume.docx",
        "medical.pdf",
        ".env",
    ],
)
def test_refuses_personal_data(path):
    result = run_checker([path])
    assert result.returncode == 1
    assert path in result.stderr


@pytest.mark.parametrize(
    "path",
    [
        "logbook/cli.py",
        "tests/fixtures/sample.csv",
        "logbook/templates/blank.csv",
        "docs/design/ARCHITECTURE.md",
        ".env.example",
    ],
)
def test_allows_code_and_samples(path):
    assert run_checker([path]).returncode == 0


def test_no_tracked_file_is_personal_data():
    tracked = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files"],
        cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    result = run_checker(tracked)
    assert result.returncode == 0, result.stderr
