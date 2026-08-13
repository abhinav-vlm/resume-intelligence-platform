from src.normalizers.education_normalizer import normalize_education,normalize_degree,normalize_duration

def test_normalize_education_score():
    education = [
        {
            "institution": "NIT Agartala",
            "duration": "2020 – 2024",
            "degree": "Bachelor of Technology",
            "cgpa": "CGPA: 8.30",
        }
    ]

    result = normalize_education(education)

    assert result[0]["score"] == 8.3
    assert result[0]["score_type"] == "CGPA"

def test_normalize_education_percentage():
    education = [
        {
            "institution": "School",
            "duration": "2019 – 2020",
            "degree": "Senior Secondary",
            "cgpa": "Percentage: 73",
        }
    ]

    result = normalize_education(education)

    assert result[0]["score"] == 73.0
    assert result[0]["score_type"] == "percentage"


def test_normalize_education_institution():
    education = [
        {
            "institution": "  NIT Agartala  ",
            "duration": "2020 – 2024",
            "degree": "Bachelor of Technology",
            "cgpa": "CGPA: 8.30",
        }
    ]

    result = normalize_education(education)

    assert result[0]["institution"] == "NIT Agartala"

def test_degree_with_in_field():
    result = normalize_degree(
        "Bachelor of Technology in Electronics and Communication Engineering"
    )

    assert result == (
        "B.Tech",
        "Electronics and Communication Engineering"
    )


def test_degree_with_comma_field():
    result = normalize_degree("B.Tech, CSE")

    assert result == (
        "B.Tech",
        "Computer Science and Engineering"
    )


def test_degree_with_dash_field():
    result = normalize_degree("BTech - CSE")

    assert result == (
        "B.Tech",
        "Computer Science and Engineering"
    )


def test_degree_with_parentheses_field():
    result = normalize_degree("B.Tech (CSE)")

    assert result == (
        "B.Tech",
        "Computer Science and Engineering"
    )


def test_degree_with_pipe_field():
    result = normalize_degree("B.Tech | CSE")

    assert result == (
        "B.Tech",
        "Computer Science and Engineering"
    )


def test_degree_without_field():
    result = normalize_degree("B.Tech")

    assert result == (
        "B.Tech",
        None
    )

def test_normalize_duration_range():
    result = normalize_duration("2020 – 2024")

    assert result == (2020, 2024)


def test_normalize_duration_single_year():
    result = normalize_duration("2020")

    assert result == (2020, None)


def test_normalize_duration_empty():
    result = normalize_duration("")

    assert result == (None, None)

def test_normalize_duration_hyphen():
    result = normalize_duration("2020 - 2024")

    assert result == (2020, 2024)

def test_normalize_education():
    education = [
        {
            "institution": "  NIT Agartala  ",
            "duration": "2020 – 2024",
            "degree": "Bachelor of Technology in ECE",
            "cgpa": "CGPA: 8.30",
        }
    ]

    result = normalize_education(education)

    assert result == [
        {
            "institution": "NIT Agartala",
            "degree": "B.Tech",
            "field": "Electronics and Communication Engineering",
            "start_year": 2020,
            "end_year": 2024,
            "score": 8.3,
            "score_type": "CGPA",
        }
    ]