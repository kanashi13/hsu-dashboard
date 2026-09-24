import re

_TERM = re.compile(r"سال\s*(?:تحصیلی)?\s*:?\s*(\d{4})\s*-\s*(\d{4})\s*نیمسال\s*:?\s*(\S+)")

SEMESTERS = {"اول": "first", "دوم": "second", "تابستان": "summer"}


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def parse_term(text: str) -> tuple[str | None, str | None]:
    match = _TERM.search(clean(text))
    if not match:
        return None, None
    academic_year = "-".join(sorted(match.group(1, 2)))
    return academic_year, SEMESTERS.get(match.group(3), match.group(3))
