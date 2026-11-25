"""Logbook: pilot logbook dashboard and CLI tools."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("logbook")
except PackageNotFoundError:  # running from a source tree that was never pip-installed
    __version__ = "0.0.0+source"
