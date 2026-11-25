from logbook import __version__
from logbook.cli import main


def test_no_command_prints_help(capsys):
    assert main([]) == 0
    assert "usage: logbook" in capsys.readouterr().out


def test_version(capsys):
    assert main(["version"]) == 0
    assert capsys.readouterr().out.strip() == f"logbook {__version__}"


def test_paths_uses_override(capsys, isolated_data_dir):
    assert main(["paths"]) == 0
    out = capsys.readouterr().out
    assert str(isolated_data_dir) in out
    assert not isolated_data_dir.exists()


def test_paths_create_makes_folders(isolated_data_dir):
    assert main(["paths", "--create"]) == 0
    for name in ("imports", "exports", "logs"):
        assert (isolated_data_dir / name).is_dir()
