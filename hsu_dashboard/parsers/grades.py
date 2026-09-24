from bs4 import BeautifulSoup

from .common import parse_term


def weighted_average(courses: list[dict]) -> tuple[float, float | None]:
    units = sum(c["units"] for c in courses)
    if not units:
        return 0.0, None
    return units, round(sum(c["units"] * c["grade"] for c in courses) / units, 2)


def parse_grades(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    academic_year, semester = parse_term(soup.find("h3").get_text())
    courses = []
    for row in soup.find("table").find_all("tr"):
        cells = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cells) >= 7 and cells[0].isdigit():
            courses.append(
                {
                    "code": cells[1],
                    "name": cells[2],
                    "units": float(cells[3]),
                    "teacher": cells[4],
                    "grade": float(cells[5]),
                    "status": cells[6],
                }
            )
    total_units, gpa = weighted_average(courses)
    return {
        "academic_year": academic_year,
        "semester": semester,
        "courses": courses,
        "total_units": total_units,
        "gpa": gpa,
    }
