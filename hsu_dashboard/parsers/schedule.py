import re

from bs4 import BeautifulSoup

from .common import clean, parse_term

DAYS = {
    "شنبه": "sat",
    "یکشنبه": "sun",
    "دوشنبه": "mon",
    "سهشنبه": "tue",
    "چهارشنبه": "wed",
    "پنجشنبه": "thu",
    "جمعه": "fri",
}
LAB_MARKER = "آزمایشگاه"
_PARITY = re.compile(r"\*\s*شروع\s*(فرد|زوج)\s*$")
_LOCATION = re.compile(r"\(([^()]*)\)\s*$")
_GROUP = re.compile(r"^(.*)\((\d+)\)$")


def parse_cell(text: str) -> dict:
    text = clean(text)
    week = "every"
    parity = _PARITY.search(text)
    if parity:
        week = "odd" if parity.group(1) == "فرد" else "even"
        text = text[: parity.start()].strip()
    location = ""
    match = _LOCATION.search(text)
    if match:
        location = match.group(1).strip()
        text = text[: match.start()].strip().rstrip(",").strip()
    parts = [p.strip() for p in text.split(",") if p.strip()]
    course, group = parts[0], ""
    grouped = _GROUP.match(course)
    if grouped:
        course, group = grouped.group(1).strip(), grouped.group(2)
    return {
        "course": course,
        "group": group,
        "teachers": parts[1:],
        "location": location or None,
        "week": week,
        "kind": "lab" if LAB_MARKER in course else "lecture",
    }


def parse_schedule(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h3")
    academic_year, semester = parse_term(heading.get_text() if heading else "")
    rows = soup.find("table").find_all("tr")
    hours = [int(th.get_text(strip=True)) for th in rows[0].find_all("th") if th.get_text(strip=True).isdigit()]
    first_hour = hours[0]
    sessions = []
    for row in rows[1:]:
        cells = row.find_all("td")
        if not cells:
            continue
        day = DAYS.get(clean(cells[0].get_text()).replace(" ", ""))
        if day is None:
            continue
        column = 0
        for cell in cells[1:]:
            span = int(cell.get("colspan", 1))
            text = cell.get_text(" ", strip=True)
            if text:
                session = parse_cell(text)
                session.update(
                    day=day,
                    start=f"{first_hour + column:02d}:00",
                    end=f"{first_hour + column + span:02d}:00",
                )
                sessions.append(session)
            column += span
    return {"academic_year": academic_year, "semester": semester, "sessions": sessions}
