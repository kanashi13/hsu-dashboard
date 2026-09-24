import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

STATIC_DIR = Path(__file__).parent / "static"


def create_app(data_path: Path) -> FastAPI:
    app = FastAPI(title="HSU Dashboard", docs_url=None, redoc_url=None)

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/data")
    def data():
        if not data_path.exists():
            return JSONResponse(
                {"error": f"No data found at {data_path}. Run 'hsu-dashboard fetch' first."}, status_code=404
            )
        return JSONResponse(json.loads(data_path.read_text(encoding="utf-8")))

    return app
