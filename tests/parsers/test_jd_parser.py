from src.parsers.jd_parser import _extract_jd, parse_jd


def test_extract_jd():
    text = """
    Machine Learning Engineer

    Python
    3+ years of experience

    AWS
    """

    result = _extract_jd(text)

    assert result == [
        "Machine Learning Engineer",
        "Python",
        "3+ years of experience",
        "AWS",
    ]


def test_extract_jd_removes_empty_lines_and_whitespace():
    text = """
        Python

        SQL
          AWS
    """

    result = _extract_jd(text)

    assert result == [
        "Python",
        "SQL",
        "AWS",
    ]


def test_extract_jd_empty_text():
    result = _extract_jd("")

    assert result == []


def test_parse_jd():
    text = """
    Backend Engineer
    Python
    FastAPI
    """

    result = parse_jd(text)

    assert result == [
        "Backend Engineer",
        "Python",
        "FastAPI",
    ]