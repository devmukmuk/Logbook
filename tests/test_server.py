from fastapi.testclient import TestClient

from logbook import __version__
from logbook.server.app import create_app


def client() -> TestClient:
    return TestClient(create_app())


def test_health():
    r = client().get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__}


def test_summary_without_data(isolated_data_dir):
    body = client().get("/api/summary").json()
    assert body["has_data"] is False
    assert body["data_dir"] == str(isolated_data_dir)
    assert body["totals"]["total_time"] == 0.0


def test_dashboard_page_renders():
    r = client().get("/")
    assert r.status_code == 200
    assert "<title>Logbook</title>" in r.text
    assert "No logbook data yet" in r.text


def test_static_css_served():
    assert client().get("/static/style.css").status_code == 200
