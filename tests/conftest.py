import pytest

from logbook.config import ENV_DATA_DIR


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Every test gets its own data folder, so no test ever touches real logbook data."""
    data = tmp_path / "data"
    monkeypatch.setenv(ENV_DATA_DIR, str(data))
    return data
