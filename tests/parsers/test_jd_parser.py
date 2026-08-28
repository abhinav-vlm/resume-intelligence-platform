from src.parsers.jd_parser import (
    _extract_role,
    _extract_jd,
    _extract_experience,
    _classify_skill_requirement,
    parse_jd,
)

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

def test_extract_role_from_job_title():
    jd = [
        "Job Title: Machine Learning Engineer",
        "3+ years of experience",
    ]

    assert _extract_role(jd) == "Machine Learning Engineer"


def test_extract_role_from_position():
    jd = [
        "Position: Backend Engineer",
        "Python experience required",
    ]

    assert _extract_role(jd) == "Backend Engineer"


def test_extract_role_from_role():
    jd = [
        "Role: Data Scientist",
        "SQL required",
    ]

    assert _extract_role(jd) == "Data Scientist"


def test_extract_role_case_insensitive():
    jd = [
        "JOB TITLE: ML Engineer",
    ]

    assert _extract_role(jd) == "ML Engineer"


def test_extract_role_missing():
    jd = [
        "We are looking for an experienced engineer.",
        "Python is required.",
    ]

    assert _extract_role(jd) is None

def test_extract_experience_years():
    jd = [
        "Machine Learning Engineer",
        "3 years of experience",
    ]

    assert _extract_experience(jd) == 3


def test_extract_experience_plus_years():
    jd = [
        "3+ years of experience",
    ]

    assert _extract_experience(jd) == 3


def test_extract_experience_industry():
    jd = [
        "At least 5 years of industry experience",
    ]

    assert _extract_experience(jd) == 5


def test_extract_experience_missing():
    jd = [
        "Python developer",
        "Strong SQL skills",
    ]

    assert _extract_experience(jd) is None

def test_classify_required_skill():
    assert (
        _classify_skill_requirement(
            "Required skills: Python, SQL"
        )
        == "required"
    )


def test_classify_must_have_skill():
    assert (
        _classify_skill_requirement(
            "Candidates must have Python experience"
        )
        == "required"
    )


def test_classify_optional_skill():
    assert (
        _classify_skill_requirement(
            "Nice to have: Docker and Kubernetes"
        )
        == "optional"
    )


def test_classify_preferred_skill():
    assert (
        _classify_skill_requirement(
            "AWS experience preferred"
        )
        == "optional"
    )


def test_classify_unknown_skill_requirement():
    assert (
        _classify_skill_requirement(
            "Python, SQL and AWS"
        )
        == "unknown"
    )

def test_parse_jd():
    text = """
    Job Title: Machine Learning Engineer
    3+ years of experience
    Required skills: Python, SQL
    Nice to have: Docker
    """

    result = parse_jd(text)

    assert result["role"] == "Machine Learning Engineer"
    assert result["experience"] == 3

    assert result["skill_requirements"] == [
        {
            "line": "Job Title: Machine Learning Engineer",
            "requirement": "unknown",
        },
        {
            "line": "3+ years of experience",
            "requirement": "unknown",
        },
        {
            "line": "Required skills: Python, SQL",
            "requirement": "required",
        },
        {
            "line": "Nice to have: Docker",
            "requirement": "optional",
        },
    ]