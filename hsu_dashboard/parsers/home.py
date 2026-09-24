import re

from bs4 import BeautifulSoup

from .common import clean, parse_term

_WEEK = re.compile(r"\(\s*هفته\s*(فرد|زوج)\s*\)")


def parse_home(html: str) -> dict:
    text = clean(BeautifulSoup(html, "html.parser").get_text(" "))
    academic_year, semester = parse_term(text)
    week = _WEEK.search(text)
    if academic_year is None or week is None:
        raise ValueError("Academic year and week parity were not found on the portal home page")
    return {
        "academic_year": academic_year,
        "semester": semester,
        "week": "odd" if week.group(1) == "فرد" else "even",
    }
