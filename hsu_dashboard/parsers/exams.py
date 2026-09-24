from bs4 import BeautifulSoup

from .common import clean, parse_term


def parse_exams(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h3")
    academic_year, semester = parse_term(heading.get_text() if heading else "")
    exams = []
    for row in soup.find("table").find_all("tr"):
        cells = [clean(td.get_text(" ")) for td in row.find_all("td")]
        if len(cells) < 9 or not cells[0].isdigit():
            continue
        exams.append(
            {
                "code": cells[0],
                "group": cells[1],
                "course": cells[2],
                "teacher": cells[3],
                "slot": cells[5],
                "date": cells[6] or None,
                "room": cells[7] if cells[7] not in ("", "0") else None,
                "note": cells[8] or None,
            }
        )
    return {"academic_year": academic_year, "semester": semester, "exams": exams}
