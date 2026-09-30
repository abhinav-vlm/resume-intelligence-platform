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

    assert _extract_experience(jd) == 36


def test_extract_experience_plus_years():
    jd = [
        "3+ years of experience",
    ]

    assert _extract_experience(jd) == 36


def test_extract_experience_industry():
    jd = [
        "At least 5 years of industry experience",
    ]

    assert _extract_experience(jd) == 60


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

    Requirements:
    Python
    SQL

    Preferred qualifications:
    Docker
    """

    result = parse_jd(text)

    assert result["role"] == "Machine Learning Engineer"
    assert result["experience_months"] == 36

    # skill_requirements is list[{skill, requirement}] under current contract
    skills_map = {
        r["skill"]: r["requirement"]
        for r in result["skill_requirements"]
    }
    assert skills_map["Python"] == "required"
    assert skills_map["SQL"] == "required"
    assert skills_map["Docker"] == "optional"

def test_extract_skills_from_sentence():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": (
                "We need a Python developer with FastAPI experience.\n"
                "Strong SQL knowledge is required."
            ),
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQL" in skills

def test_extract_skills_case_insensitive():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Experience with PYTHON and fastapi.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "Python" in skills
    assert "FastAPI" in skills

def test_extract_skills_deduplicates():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Python developer.\nStrong Python experience.\nPython is required.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert skills == ["Python"]

def test_extract_unknown_skill_is_preserved():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Experience with LangChain.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "LangChain" in skills

def test_extract_skills_does_not_match_partial_word():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Pythonic programming practices are useful.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert skills == []

def test_extract_multiple_skills_from_one_line():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Build backend services using Python, FastAPI, SQL and Docker.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "SQL" in skills
    assert "Docker" in skills

def test_extract_cpp_without_extracting_c():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Strong C++ development experience.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "C++" in skills
    assert "C" not in skills

def test_extract_mysql_without_extracting_sql():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Experience with MySQL databases.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "MySQL" in skills
    assert "SQL" not in skills

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

    assert "Python" in result["skills"]
    assert "FastAPI" in result["skills"]
    assert "SQL" in result["skills"]
def test_extract_skill_specific_experience():
    jd = [
        "3 years of Python experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "Python",
            "experience_months": 36,
        }
    ]
def test_extract_multiple_skill_specific_experience():
    jd = [
        "3 years of Python experience and 2 years of AWS experience"
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {"skill": "Python", "experience_months": 36},
        {"skill": "AWS", "experience_months": 24},
    ]

def test_extract_skill_specific_experience_plus_years():
    jd = [
        "5+ years of FastAPI experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "FastAPI",
            "experience_months": 60,
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
            "experience_months": 48,
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
            "experience_months": 36,
        },
        {
            "skill": "AWS",
            "experience_months": 60,
        },
        {
            "skill": "FastAPI",
            "experience_months": 24,
        },
    ]

def test_extract_skill_specific_experience_unknown_skill():
    jd = [
        "4 years of stakeholder management experience",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == []

def test_filter_noise_section():
    """
    Sections with a noise canonical name are removed;
    all others are preserved regardless of order.
    """
    sections = [
        {
            "name": "preamble",
            "original_name": None,
            "text": "Role: Backend Engineer",
        },
        {
            "name": "COMPANY_INFO",
            "original_name": "about the company",
            "text": "We build amazing products.\nPython",
        },
        {
            "name": "REQUIREMENTS",
            "original_name": "required skills",
            "text": "",
        },
    ]

    result = _filter_noise_sections(sections)
    names = [s["name"] for s in result]

    assert "COMPANY_INFO" not in names
    assert "preamble" in names
    assert "REQUIREMENTS" in names


def test_filter_noise_section_case_insensitive():
    """
    Filtering operates on canonical names (upper-cased by the detector),
    so case of the original header text is irrelevant.
    """
    sections = [
        {
            "name": "preamble",
            "original_name": None,
            "text": "Role: Backend Engineer",
        },
        {
            "name": "COMPANY_INFO",
            "original_name": "about the company",
            "text": "We build amazing products.",
        },
        {
            "name": "REQUIREMENTS",
            "original_name": "required skills",
            "text": "Python",
        },
    ]

    result = _filter_noise_sections(sections)
    names = [s["name"] for s in result]

    assert "COMPANY_INFO" not in names
    assert "preamble" in names
    assert "REQUIREMENTS" in names


def test_filter_noise_section_at_end():
    """
    Noise sections at the end are dropped; they do not consume
    following content under the structured-section architecture.
    """
    sections = [
        {
            "name": "preamble",
            "original_name": None,
            "text": "Role: Backend Engineer\nPython",
        },
        {
            "name": "COMPANY_INFO",
            "original_name": "about the company",
            "text": "We build amazing products.\nWe have offices globally",
        },
    ]

    result = _filter_noise_sections(sections)
    names = [s["name"] for s in result]

    assert "COMPANY_INFO" not in names
    assert "preamble" in names

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
    assert result["experience_months"] == 36

    assert "Python" in result["skills"]
    assert "AWS" in result["skills"]

def test_extract_overall_experience_ignores_skill_specific_experience():
    jd = [
        "4 years of experience with SQL",
        "3+ years of professional industry experience",
    ]

    result = _extract_experience(jd)

    assert result == 36

def test_extract_overall_experience_ignores_skill_specific_experience_reversed():
    jd = [
        "3+ years of professional industry experience",
        "4 years of experience with SQL",
    ]

    result = _extract_experience(jd)

    assert result == 36

def test_extract_overall_experience_ignores_skill_specific_experience():
    jd = [
        "4 years of experience with SQL",
        "3+ years of professional industry experience",
    ]

    result = _extract_experience(jd)

    assert result == 36
def test_extract_overall_experience_ignores_skill_specific_experience_when_overall_comes_first():
    jd = [
        "3+ years of professional industry experience",
        "4 years of experience with SQL",
    ]

    result = _extract_experience(jd)

    assert result == 36

def test_extract_experience_returns_none_when_only_skill_specific_experience_exists():
    jd = [
        "4 years of experience with SQL",
        "3 years of Python experience",
    ]

    result = _extract_experience(jd)

    assert result is None

def test_extract_role_stops_at_noise_section():
    """
    Under the current architecture, noise filtering is performed on
    structured sections before role extraction — noise content never
    reaches _extract_role.  _extract_role itself simply reads the first
    colon-delimited role keyword line from already-clean JD lines.
    """
    jd = [
        "Job Title: Senior Backend / ML Engineer",
    ]

    result = _extract_role(jd)

    assert result == "Senior Backend / ML Engineer"

def test_extract_role():
    jd = [
        "Job Title: Senior Backend / ML Engineer"
    ]

    result = _extract_role(jd)

    assert result == "Senior Backend / ML Engineer"

def test_parse_jd_experience_in_months():
    text = """
    Role: Machine Learning Engineer
    Minimum 3 years of experience
    """

    result = parse_jd(text)

    assert result["experience_months"] == 36

def test_parse_jd_skill_experience_in_months():
    text = """
    Role: Machine Learning Engineer
    2 years experience with Python
    """

    result = parse_jd(text)

    assert result["skill_specific_experience"] == [
        {
            "skill": "Python",
            "experience_months": 24,
        }
    ]

def test_extract_skill_specific_experience_without_of():
    jd = [
        "2 years experience with Python",
    ]

    result = _extract_skill_specific_experience(jd)

    assert result == [
        {
            "skill": "Python",
            "experience_months": 24,
        }
    ]

def test_extract_known_and_unknown_skills():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Experience with Python, PyTorch, LangChain and Jupyter.",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "Python" in skills
    assert "PyTorch" in skills
    assert "LangChain" in skills
    assert "Jupyter" in skills

def test_extract_unknown_skills_deduplicates():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "LangChain\nlangchain\nLANGCHAIN",
        }
    ]

    skills, _ = _extract_skills(sections)

    assert skills == ["LangChain"]

def test_extract_data_science_skills():
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": (
                "TensorFlow, PyTorch, Scikit-learn, Pandas\n"
                "NumPy, Jupyter, Python, SQL"
            ),
        }
    ]

    skills, _ = _extract_skills(sections)

    assert "TensorFlow" in skills
    assert "PyTorch" in skills
    assert "Scikit-learn" in skills
    assert "Pandas" in skills
    assert "NumPy" in skills
    assert "Jupyter" in skills
    assert "Python" in skills
    assert "SQL" in skills


# ------------------------------------------------------------------
# Requirement classification from section context
# ------------------------------------------------------------------

def test_extract_skills_requirement_from_requirements_section():
    """
    Skills in a REQUIREMENTS section default to 'required'
    when the line carries no explicit override signal.
    """
    sections = [
        {
            "name": "REQUIREMENTS",
            "original_name": "requirements",
            "text": "Python\nFastAPI",
        }
    ]

    _, skill_requirements = _extract_skills(sections)

    req_map = {r["skill"]: r["requirement"] for r in skill_requirements}
    assert req_map["Python"] == "required"
    assert req_map["FastAPI"] == "required"


def test_extract_skills_requirement_from_preferred_section():
    """
    Skills in a PREFERRED_QUALIFICATIONS section default to 'optional'.
    """
    sections = [
        {
            "name": "PREFERRED_QUALIFICATIONS",
            "original_name": "preferred qualifications",
            "text": "Docker\nKubernetes",
        }
    ]

    _, skill_requirements = _extract_skills(sections)

    req_map = {r["skill"]: r["requirement"] for r in skill_requirements}
    assert req_map["Docker"] == "optional"
    assert req_map["Kubernetes"] == "optional"

