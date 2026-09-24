import json
from pathlib import Path

from fastapi.testclient import TestClient

from hsu_dashboard.server import create_app

SAMPLE = Path(__file__).resolve().parents[1] / "examples" / "data.sample.json"


def test_api_serves_data_and_index():
    client = TestClient(create_app(SAMPLE))
    assert client.get("/api/data").json() == json.loads(SAMPLE.read_text(encoding="utf-8"))
    assert "HSU Student Dashboard" in client.get("/").text


def test_api_reports_missing_data(tmp_path):
    response = TestClient(create_app(tmp_path / "missing.json")).get("/api/data")
    assert response.status_code == 404 and "hsu-dashboard fetch" in response.json()["error"]
