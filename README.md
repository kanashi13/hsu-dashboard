# HSU Student Dashboard

A small command-line tool and web dashboard for HSU students. It pulls your schedule, exams, grades, and transcript from the university portal, saves them as JSON, and shows them in a simple English interface. Course names and instructors stay in Persian and are displayed right-to-left.

Not affiliated with HSU. Use it with your own account only. Don't commit your real data to a public repo — see the note at the bottom.

I built this because the portal is annoying on mobile and I wanted a quick way to check my week without logging in every time.

## What it does

- `hsu-dashboard fetch` logs in and saves your data as JSON.
- `hsu-dashboard serve` starts a local web dashboard.
- Days are stored as `sat`, `sun`, etc. Class types are `lecture` or `lab`. Academic years are sorted correctly (the portal shows them reversed, like `1406-1405`).
- You can run the dashboard with fake data if you just want to see how it looks:
  ```bash
  hsu-dashboard serve --data examples/data.sample.json
  ```

## Install

Needs Python 3.10 or newer.

```bash
git clone https://github.com/<your-username>/hsu-student-dashboard.git
cd hsu-student-dashboard

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
```

For tests and development:

```bash
pip install -e ".[dev]"
```

## Usage

Fetch your data:

```bash
hsu-dashboard fetch --username <student-id>
```

It'll ask for your password. The JSON files go into `data/`, which is git-ignored.

Some flags:

- `--out DIR` — where to save (default `data/`)
- `--only schedule,exams` — fetch just some sections

Serve the dashboard:

```bash
hsu-dashboard serve
```

Open http://127.0.0.1:8000. By default it reads from `data/`. You can point it somewhere else:

```bash
hsu-dashboard serve --data examples/data.sample.json
```

Other flags: `--host`, `--port`.

## Data format

Each section is a JSON file. Here's a small example:

```json
{
  "schedule": [
    {
      "day": "sat",
      "start": "08:00",
      "end": "10:00",
      "course": "ریاضی ۱",
      "instructor": "دکتر …",
      "type": "lecture",
      "location": "کلاس ۲۰۱"
    }
  ],
  "exams": [
    { "date": "1404-03-20", "time": "10:00", "course": "ریاضی ۱", "room": "سالن ۱" }
  ],
  "grades": {
    "term": "1403-1404-2",
    "gpa": 17.74,
    "courses": [ { "name": "ریاضی ۱", "credits": 3, "grade": 18.5 } ]
  },
  "transcript": {
    "terms": [ { "term": "1403-1404-1", "gpa": 17.5, "courses": [] } ],
    "overall": { "gpa": 17.64, "passed_credits": 32 }
  }
}
```

There's a full fake example in `examples/data.sample.json`.

## Tests

```bash
pytest
```

- `tests/test_parsers.py` — parser tests with made-up HTML, no login needed.
- `tests/test_api.py` — API tests using FastAPI's TestClient against the sample data.

## Privacy

This thing handles personal data. So:

- Don't commit `data/` or any saved HTML from the portal.
- The default `.gitignore` already excludes `data/`, `*.html`, and `.env`.
- Before you push, run `git status` and make sure nothing personal is staged.

## Layout

```
hsu-student-dashboard/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── hsu_dashboard/
│   ├── cli.py
│   ├── fetcher.py
│   ├── server.py
│   ├── parsers/
│   │   ├── common.py
│   │   ├── home.py
│   │   ├── schedule.py
│   │   ├── exams.py
│   │   ├── grades.py
│   │   └── transcript.py
│   └── static/
│       └── index.html
├── examples/
│   └── data.sample.json
└── tests/
    ├── test_parsers.py
    └── test_api.py
```

## License

MIT. See `LICENSE`.