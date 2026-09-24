from hsu_dashboard.parsers import parse_exams, parse_grades, parse_home, parse_schedule, parse_transcript
from hsu_dashboard.parsers.grades import weighted_average

HOME = "<html><body>User: 000 سال تحصیلی: 1406-1405&nbsp;نیمسال&nbsp;اول&nbsp;(هفته فرد)</body></html>"

SCHEDULE = """
<h3>برنامه هفتگي در سال 1406- 1405 نیمسال اول</h3>
<table>
<tr><th></th><th>8</th><th>9</th><th>10</th><th>11</th></tr>
<tr><td>شنبه</td>
<td colspan="2">آزمایشگاه زیست(1), Smith, (Room 1)</td>
<td> </td>
<td colspan="1">Genetics(2), Doe, (Room 2)* شروع فرد</td></tr>
<tr><td>سه شنبه</td><td colspan="1">Physics(1), Roe, ()</td></tr>
</table>
"""

GRADES = """
<h3>اطلاعیه نمرات در سال 1405- 1404 نیمسال دوم</h3>
<table>
<tr><th>ردیف</th></tr>
<tr><td>1</td><td>100</td><td>Course A</td><td>2.00</td><td>Teacher</td><td>18.00</td><td>عادی</td></tr>
<tr><td>2</td><td>101</td><td>Course B</td><td>1.00</td><td>Teacher</td><td>15.00</td><td>عادی</td></tr>
</table>
"""

EXAMS = """
<h3>برنامه امتحاني در سال 1406- 1405 نیمسال اول</h3>
<table>
<tr><th>شماره درس</th></tr>
<tr><td>851038</td><td>2</td><td>Lab</td><td>Doe</td><td>صفرم</td><td>6</td><td> </td><td>0</td><td>Held as a workshop&nbsp;</td></tr>
<tr><td>851037</td><td>1</td><td>Genetics</td><td>Doe</td><td>یکم</td><td>10</td><td>1405/10/19</td><td>0</td><td>&nbsp;</td></tr>
</table>
"""

TRANSCRIPT = """
سال : 1404-1403&nbsp; نیمسال : اول
<table><tr><th>ردیف</th><th>شماره درس</th><th>نام درس</th><th>واحد</th><th>نمره</th></tr>
<tr><td>1</td><td>100</td><td>Course A</td><td>3.00</td><td>17.00</td></tr></table>
<b>واحد اخذ شده ترم : 3 واحد قبول شده ترم : 3 معدل ترم : 17.00<br>واحد اخذ شده کل: 3 واحد قبول شده کل: 3 معدل کل : 17.00</b>
"""


def test_home_reads_year_semester_and_week():
    assert parse_home(HOME) == {"academic_year": "1405-1406", "semester": "first", "week": "odd"}


def test_home_requires_header():
    try:
        parse_home("<html></html>")
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_schedule_uses_colspan_for_time_and_detects_parity():
    result = parse_schedule(SCHEDULE)
    lab, genetics, physics = result["sessions"]
    assert (lab["day"], lab["start"], lab["end"], lab["kind"]) == ("sat", "08:00", "10:00", "lab")
    assert (genetics["start"], genetics["end"], genetics["week"], genetics["location"]) == ("11:00", "12:00", "odd", "Room 2")
    assert (physics["day"], physics["location"]) == ("tue", None)
    assert result["academic_year"] == "1405-1406"


def test_grades_weighted_average():
    result = parse_grades(GRADES)
    assert result["total_units"] == 3
    assert result["gpa"] == 17.0
    assert (result["academic_year"], result["semester"]) == ("1404-1405", "second")
    assert weighted_average([]) == (0.0, None)


def test_exams_handle_missing_date_and_room():
    exams = parse_exams(EXAMS)["exams"]
    assert exams[0]["date"] is None and exams[0]["note"] == "Held as a workshop"
    assert exams[1]["date"] == "1405/10/19" and exams[1]["room"] is None


def test_transcript_terms_and_cumulative_values():
    result = parse_transcript(TRANSCRIPT)
    term = result["terms"][0]
    assert (term["academic_year"], term["semester"], term["term_gpa"]) == ("1403-1404", "first", 17.0)
    assert result["cumulative_gpa"] == 17.0 and result["units_passed"] == 3
