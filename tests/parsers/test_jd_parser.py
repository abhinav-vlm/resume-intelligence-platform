from src.parsers.jd_parser import (
    _extract_role,
    _extract_jd,
    _extract_experience,
    _classify_skill_requirement,
    _extract_skill_specific_experience,
    parse_jd,
    _filter_noise_sections,
    _resolve_skill_overlaps,
    _extract_skills
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

def test_extract_skills_from_sentence():
    jd = [
        "We need a Python developer with FastAPI experience.",
        "Strong SQL knowledge is required.",
    ]

    result = _extract_skills(jd)

    assert result == ["Python", "FastAPI", "SQL"]

def test_extract_skills_case_insensitive():
    jd = [
        "Experience with PYTHON and fastapi.",
    ]

    result = _extract_skills(jd)

    assert result == ["Python", "FastAPI"]

def test_extract_skills_deduplicates():
    jd = [
        "Python developer.",
        "Strong Python experience.",
        "Python is required.",
    ]

    result = _extract_skills(jd)

    assert result == ["Python"]

def test_extract_unknown_skill_is_ignored():
    jd = [
        "Experience with stakeholder management.",
    ]

    result = _extract_skills(jd)

    assert result == []

def test_extract_skills_does_not_match_partial_word():
    jd = [
        "Pythonic programming practices are useful.",
    ]

    result = _extract_skills(jd)

    assert result == []

def test_extract_multiple_skills_from_one_line():
    jd = [
        "Build backend services using Python, FastAPI, SQL and Docker."
    ]

    result = _extract_skills(jd)

    assert result == [
        "Python",
        "FastAPI",
        "SQL",
        "Docker",
    ]

def test_extract_cpp_without_extracting_c():
    jd = [
        "Strong C++ development experience."
    ]

    result = _extract_skills(jd)

    assert result == ["C++"]

def test_extract_mysql_without_extracting_sql():
    jd = [
        "Experience with MySQL databases."
    ]

    result = _extract_skills(jd)

    assert result == ["MySQL"]

def test_resolve_overlapping_skills_keeps_longer_match():
    matches = [
        {"skill": "C++", "line": 0, "start": 0, "end": 3},
        {"skill": "C", "line": 0, "start": 0, "end": 1},
    ]

    assert _resolve_skill_overlaps(matches) == [
        {"skill": "C++", "line": 0, "start": 0, "end": 3},
    ]

def test_resolve_non_overlapping_skills():
    matches = [
        {"skill": "Python", "line": 0, "start": 0, "end": 6},
        {"skill": "FastAPI", "line": 0, "start": 11, "end": 18},
    ]

    assert _resolve_skill_overlaps(matches) == [
        {"skill": "Python", "line": 0, "start": 0, "end": 6},
        {"skill": "FastAPI", "line": 0, "start": 11, "end": 18},
    ]

def test_parse_jd_extracts_skills():
    jd = """
    Role: Backend Engineer
    We need someone experienced with Python and FastAPI.
    SQL knowledge is required.
    """

    result = parse_jd(jd)

    assert result["skills"] == [
        "Python",
        "FastAPI",
        "SQL",
    ]
def test_extract_skill_specific_experience():
    jd = [
        "3 years of Python experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "Python",
            "experience": 3,
        }
    ]
def test_extract_multiple_skill_specific_experience():
    jd = [
        "3 years of Python experience and 2 years of AWS experience"
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {"skill": "Python", "experience": 3},
        {"skill": "AWS", "experience": 2},
    ]

def test_extract_skill_specific_experience_plus_years():
    jd = [
        "5+ years of FastAPI experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "FastAPI",
            "experience": 5,
        }
    ]

def test_extract_skill_specific_experience_with_skill():
    jd = [
        "4 years of experience with Python",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "Python",
            "experience": 4,
        }
    ]

def test_extract_skill_specific_experience_multiple_lines():
    jd = [
        "3 years of Python experience",
        "5+ years of AWS experience",
        "2 years of experience with FastAPI",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "Python",
            "experience": 3,
        },
        {
            "skill": "AWS",
            "experience": 5,
        },
        {
            "skill": "FastAPI",
            "experience": 2,
        },
    ]

def test_extract_skill_specific_experience_unknown_skill():
    jd = [
        "4 years of stakeholder management experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == []

def test_filter_noise_section():
    jd = [
        "Role: Backend Engineer",
        "About the company",
        "We build amazing products.",
        "Python",
        "Required skills:",
    ]

    result = _filter_noise_sections(jd)

    assert result == [
        "Role: Backend Engineer",
        "Required skills:",
    ]

def test_filter_noise_section_case_insensitive():
    jd = [
        "Role: Backend Engineer",
        "ABOUT THE COMPANY",
        "We build amazing products.",
        "Required skills:",
        "Python",
    ]

    result = _filter_noise_sections(jd)

    assert result == [
        "Role: Backend Engineer",
        "Required skills:",
        "Python",
    ]

def test_filter_noise_section_at_end():
    jd = [
        "Role: Backend Engineer",
        "Python",
        "About the company",
        "We build amazing products.",
        "We have offices globally",
    ]

    result = _filter_noise_sections(jd)

    assert result == [
        "Role: Backend Engineer",
        "Python",
    ]

def test_parse_jd_filters_noise_and_extracts_data():
    text = """
    Role: Backend Engineer
    3+ years of experience
    3 years of Python experience
    2 years of AWS experience

    About the company
    We build amazing products.
    Python is mentioned here but should be ignored.

    Required skills:
    Python
    AWS
    """

    result = parse_jd(text)

    assert result["role"] == "Backend Engineer"
    assert result["experience"] == 3

    assert result["skills"] == [
        "Python",
        "AWS",
    ]

def test_extract_overall_experience_ignores_skill_specific_experience():
    jd = [
        "4 years of experience with SQL",
        "3+ years of professional industry experience",
    ]

    result = _extract_experience(jd)

    assert result == 3

def test_extract_overall_experience_ignores_skill_specific_experience_reversed():
    jd = [
        "3+ years of professional industry experience",
        "4 years of experience with SQL",
    ]

    result = _extract_experience(jd)

    assert result == 3

def test_extract_overall_experience_ignores_skill_specific_experience():
    jd = [
        "4 years of experience with SQL",
        "3+ years of professional industry experience",
    ]

    result = _extract_experience(jd)

    assert result == 3
def test_extract_overall_experience_ignores_skill_specific_experience_when_overall_comes_first():
    jd = [
        "3+ years of professional industry experience",
        "4 years of experience with SQL",
    ]

    result = _extract_experience(jd)

    assert result == 3

def test_extract_experience_returns_none_when_only_skill_specific_experience_exists():
    jd = [
        "4 years of experience with SQL",
        "3 years of Python experience",
    ]

    result = _extract_experience(jd)

    assert result is None

def test_extract_role_stops_at_noise_section():
    jd = [
        "Job Title: Senior Backend / ML Engineer  About the company We are a fast-growing"
    ]

    result = _extract_role(jd)

    assert result == "Senior Backend / ML Engineer"

def test_extract_role():
    jd = [
        "Job Title: Senior Backend / ML Engineer"
    ]

    result = _extract_role(jd)

    assert result == "Senior Backend / ML Engineer"