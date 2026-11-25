"""Where Logbook keeps its files.

All personal data lives under one data folder that git never tracks:

    <data dir>/
        imports/   raw files from other logbooks, as received
        exports/   files Logbook generates (summaries, application breakdowns)
        logs/      run logs

The default is ``data/`` at the repository root (git-ignored). Set the
``LOGBOOK_DATA_DIR`` environment variable to keep it anywhere else, such as
an encrypted vault.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ENV_DATA_DIR = "LOGBOOK_DATA_DIR"
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = REPO_ROOT / "data"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


@dataclass(frozen=True)
class Paths:
    data: Path

    @property
    def imports(self) -> Path:
        return self.data / "imports"

    @property
    def exports(self) -> Path:
        return self.data / "exports"

    @property
    def logs(self) -> Path:
        return self.data / "logs"

    def ensure(self) -> "Paths":
        for folder in (self.data, self.imports, self.exports, self.logs):
            folder.mkdir(parents=True, exist_ok=True)
        return self


def get_paths() -> Paths:
    override = os.environ.get(ENV_DATA_DIR)
    return Paths(Path(override).expanduser().resolve() if override else DEFAULT_DATA_DIR)
