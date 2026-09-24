import re

from bs4 import BeautifulSoup

from .common import clean, parse_term

_HEADER = re.compile(r"سال\s*:\s*\d{4}")


def _number(label: str, text: str) -> float:
    return float(re.search(label + r"\s*:\s*([\d.]+)", text).group(1))


def parse_transcript(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    terms = []
    for table in soup.find_all("table"):
        headings = [th.get_text(strip=True) for th in table.find_all("th")]
        if "نمره" not in headings or "نام درس" not in headings:
            continue
        academic_year, semester = parse_term(table.find_previous(string=_HEADER))
        summary = clean(table.find_next("b").get_text(" "))
        courses = []
        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) >= 5 and cells[0].isdigit():
                courses.append(
                    {"code": cells[1], "name": cells[2], "units": float(cells[3]), "grade": float(cells[4])}
                )
        terms.append(
            {
                "academic_year": academic_year,
                "semester": semester,
                "courses": courses,
                "units_taken": _number("واحد اخذ شده ترم", summary),
                "units_passed": _number("واحد قبول شده ترم", summary),
                "term_gpa": _number("معدل ترم", summary),
                "cumulative_units_taken": _number("واحد اخذ شده کل", summary),
                "cumulative_units_passed": _number("واحد قبول شده کل", summary),
                "cumulative_gpa": _number("معدل کل", summary),
            }
        )
    last = terms[-1] if terms else None
    return {
        "terms": terms,
        "cumulative_gpa": last["cumulative_gpa"] if last else None,
        "units_passed": last["cumulative_units_passed"] if last else 0,
    }
