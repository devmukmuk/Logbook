"""The `logbook` command.

Each tool is a subcommand. To add one, write a ``_cmd_<name>(args) -> int``
function and register it in ``build_parser``.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from logbook import __version__
from logbook.config import DEFAULT_HOST, DEFAULT_PORT, ENV_DATA_DIR, get_paths


def _cmd_version(args: argparse.Namespace) -> int:
    print(f"logbook {__version__}")
    return 0


def _cmd_paths(args: argparse.Namespace) -> int:
    paths = get_paths()
    if args.create:
        paths.ensure()
    print(f"data     {paths.data}")
    print(f"imports  {paths.imports}")
    print(f"exports  {paths.exports}")
    print(f"logs     {paths.logs}")
    print(f"(override the data folder with {ENV_DATA_DIR})")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn  # imported here so the other subcommands start fast

    url = f"http://{args.host}:{args.port}/"
    print(f"Logbook dashboard on {url}  (Ctrl+C to stop)")
    if args.open:
        import threading
        import webbrowser

        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    uvicorn.run(
        "logbook.server.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logbook",
        description="Pilot logbook tools and local dashboard.",
    )
    parser.add_argument("--version", action="version", version=f"logbook {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p = sub.add_parser("version", help="print the version")
    p.set_defaults(func=_cmd_version)

    p = sub.add_parser("paths", help="show where Logbook keeps its data")
    p.add_argument("--create", action="store_true", help="create the folders if missing")
    p.set_defaults(func=_cmd_paths)

    p = sub.add_parser("serve", help="run the local dashboard server")
    p.add_argument("--host", default=DEFAULT_HOST, help=f"bind address (default {DEFAULT_HOST})")
    p.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port (default {DEFAULT_PORT})")
    p.add_argument("--open", action="store_true", help="open the dashboard in a browser")
    p.add_argument("--reload", action="store_true", help="restart on code changes (development)")
    p.set_defaults(func=_cmd_serve)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
