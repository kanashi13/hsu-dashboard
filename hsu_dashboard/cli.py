import argparse
import json
from pathlib import Path

DEFAULT_DATA = Path("data") / "data.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hsu-dashboard", description="Unofficial HSU Pooya student dashboard")
    commands = parser.add_subparsers(dest="command", required=True)

    fetch = commands.add_parser("fetch", help="Log in through a browser and build the data file")
    fetch.add_argument("--from-dir", type=Path, help="Build from saved HTML pages instead of using a browser")
    fetch.add_argument("--out", type=Path, default=DEFAULT_DATA, help="Output JSON path")

    serve = commands.add_parser("serve", help="Serve the dashboard locally")
    serve.add_argument("--data", type=Path, default=DEFAULT_DATA, help="JSON data file to display")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "fetch":
        from .fetcher import fetch_live, load_from_dir

        payload = load_from_dir(args.from_dir) if args.from_dir else fetch_live()
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved {args.out} (week: {payload['week']}, GPA: {payload['grades']['gpa']})")
    else:
        import uvicorn

        from .server import create_app

        uvicorn.run(create_app(args.data), host=args.host, port=args.port)
