from datetime import datetime
from pathlib import Path

from .parsers import parse_exams, parse_grades, parse_home, parse_schedule, parse_transcript

BASE_URL = "https://pooya.hsu.ac.ir"
SCHEDULE_URL = f"{BASE_URL}/educ/educfac/ShowStSchedule.php"
PAGE_TITLES = {
    "schedule": "Student schedule",
    "grades": "Student Grades",
    "exams": "Show Exam Days",
}
TRANSCRIPT_URL_PART = "ShowEducationalLog.php"
DUMP_FILES = {
    "home": "home.html",
    "schedule": "schedule.html",
    "grades": "grades.html",
    "exams": "exams.html",
    "transcript": "transcript.html",
}


def build_payload(pages: dict[str, str | None]) -> dict:
    home = parse_home(pages["home"])
    transcript = pages.get("transcript")
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "week": home["week"],
        "home": home,
        "schedule": parse_schedule(pages["schedule"]),
        "exams": parse_exams(pages["exams"])["exams"],
        "grades": parse_grades(pages["grades"]),
        "transcript": parse_transcript(transcript) if transcript else None,
    }


def load_from_dir(directory: Path) -> dict:
    pages = {}
    for key, name in DUMP_FILES.items():
        path = Path(directory) / name
        pages[key] = path.read_text(encoding="utf-8") if path.exists() else None
    missing = [DUMP_FILES[k] for k in ("home", "schedule", "grades", "exams") if not pages[k]]
    if missing:
        raise FileNotFoundError(f"Missing required files in {directory}: {', '.join(missing)}")
    return build_payload(pages)


def _frame_html(context, predicate):
    for page in context.pages:
        for frame in page.frames:
            try:
                if predicate(frame):
                    return frame.content()
            except Exception:
                continue
    return None


def _title_is(title: str):
    return lambda frame: frame.evaluate("document.title") == title


def _url_contains(part: str):
    return lambda frame: part in frame.url


def _wait_for_page(context, label: str, predicate, attempts: int = 3) -> str:
    for _ in range(attempts):
        input(f"Open '{label}' in the portal, wait for it to load, then press Enter... ")
        html = _frame_html(context, predicate)
        if html:
            return html
        print(f"Could not find the '{label}' page. Try again.")
    raise SystemExit(f"The '{label}' page was not found.")


def fetch_live() -> dict:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(BASE_URL)
        input("Log in (student number, password, captcha). Press Enter once the portal home page is shown... ")
        home = page.content()
        schedule_page = context.new_page()
        schedule_page.goto(SCHEDULE_URL)
        schedule = schedule_page.content()
        if PAGE_TITLES["schedule"] not in schedule:
            schedule = _wait_for_page(context, "Weekly schedule", _title_is(PAGE_TITLES["schedule"]))
        grades = _wait_for_page(context, "Grades", _title_is(PAGE_TITLES["grades"]))
        exams = _wait_for_page(context, "Exam schedule", _title_is(PAGE_TITLES["exams"]))
        transcript = _wait_for_page(context, "Educational log (full transcript)", _url_contains(TRANSCRIPT_URL_PART))
        browser.close()
    return build_payload(
        {"home": home, "schedule": schedule, "grades": grades, "exams": exams, "transcript": transcript}
    )
