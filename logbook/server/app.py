"""FastAPI app for the local dashboard.

Pages are server-rendered Jinja2 templates; data for charts comes from the
``/api/*`` JSON endpoints so the same numbers are available to the CLI and
to tests. The server binds to 127.0.0.1 by default and has no login: it is a
single-user, local-only tool.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from logbook import __version__
from logbook.config import get_paths

HERE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=HERE / "templates")


def _summary() -> dict:
    """Totals shown on the dashboard. Placeholder until the DATA epic lands."""
    paths = get_paths()
    return {
        "has_data": False,
        "data_dir": str(paths.data),
        "totals": {"total_time": 0.0, "pic": 0.0, "cross_country": 0.0, "night": 0.0, "instrument": 0.0},
    }


def create_app() -> FastAPI:
    app = FastAPI(title="Logbook", version=__version__, docs_url="/api/docs", redoc_url=None)
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        return templates.TemplateResponse(
            request, "dashboard.html", {"version": __version__, "summary": _summary()}
        )

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok", "version": __version__}

    @app.get("/api/summary")
    def summary() -> dict:
        return _summary()

    return app
