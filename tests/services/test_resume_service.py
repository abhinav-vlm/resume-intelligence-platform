import pytest

from src.parsers.skills_parser import extract_skills
from src.normalizers.skill_normalizer import normalize_skills


# ============================================================
# Basic extraction
# ============================================================

def test_plain_skill_lines():
    text = """
    Python
    React
    SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_comma_separated_skill_line():
    text = """
    Python, React, SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_pipe_separated_skills():
    text = """
    Python | React | SQL | Docker
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
        "Docker",
    ]

    assert result["unknown"] == []


def test_categorized_skill_lines():
    text = """
    Programming Languages: Python, Java
    Frameworks: React, Django
    Databases: SQL, MongoDB
    """

    result = extract_skills(text)

    assert "Python" in result["known"]
    assert "Java" in result["known"]
    assert "React" in result["known"]
    assert "Django" in result["known"]
    assert "SQL" in result["known"]

    assert "MongoDB" in result["unknown"]


# ============================================================
# Deduplication
# ============================================================

def test_duplicate_skills():
    text = """
    Python, React
    Python, SQL
    React
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_unknown_duplicates_are_deduplicated():
    text = """
    MongoDB
    mongodb
    MONGODB
    """

    result = extract_skills(text)

    assert result["unknown"] == [
        "MongoDB",
    ]


# ============================================================
# Skill boundary matching
# ============================================================

def test_skill_boundary_matching():
    text = """
    Python
    Pythonic
    Py
    SQL
    SQLAlchemy
    """

    result = extract_skills(text)

    assert "Python" in result["known"]
    assert "SQL" in result["known"]

    assert "Pythonic" in result["unknown"]
    assert "SQLAlchemy" in result["unknown"]


# ============================================================
# Aliases
# ============================================================

def test_skill_aliases_are_extracted():
    text = """
    ReactJS
    Express.JS
    Next.JS
    """

    result = extract_skills(text)

    assert result["known"] == [
        "ReactJS",
        "Express.JS",
        "Next.JS",
    ]


def test_known_skills_are_normalized_after_extraction():
    text = """
    Python
    ReactJS
    Express.JS
    Next.JS
    """

    result = extract_skills(text)

    normalized = normalize_skills(result["known"])

    assert result["known"] == [
        "Python",
        "ReactJS",
        "Express.JS",
        "Next.JS",
    ]

    assert normalized == [
        "Python",
        "React",
        "Express.js",
        "Next.js",
    ]

    assert result["unknown"] == []


# ============================================================
# Unknown skills
# ============================================================

def test_unknown_skills_are_preserved():
    text = """
    Python
    React
    MongoDB
    PyTorch
    LangChain
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
    ]

    assert result["unknown"] == [
        "MongoDB",
        "PyTorch",
        "LangChain",
    ]


def test_unknown_skills_in_categorized_lines():
    text = """
    Databases: MongoDB, Redis
    Frameworks: React, PyTorch
    """

    result = extract_skills(text)

    assert "React" in result["known"]

    assert result["unknown"] == [
        "MongoDB",
        "Redis",
        "PyTorch",
    ]


def test_unknown_skills_are_not_normalized():
    text = """
    Python
    MongoDB
    PyTorch
    """

    result = extract_skills(text)

    normalized = normalize_skills(result["known"])

    assert normalized == [
        "Python",
    ]

    assert result["unknown"] == [
        "MongoDB",
        "PyTorch",
    ]


def test_multi_word_unknown_skill_is_preserved():
    text = """
    Python
    Deep Learning
    Natural Language Processing
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
    ]

    assert result["unknown"] == [
        "Deep Learning",
        "Natural Language Processing",
    ]


def test_mixed_known_and_unknown_skills():
    text = """
    Python, MongoDB, React, PyTorch
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
    ]

    assert result["unknown"] == [
        "MongoDB",
        "PyTorch",
    ]



def test_legitimate_long_skill_is_preserved():
    text = """
    Object Oriented Programming
    Natural Language Processing
    """

    result = extract_skills(text)

    assert result["unknown"] == [
        "Object Oriented Programming",
        "Natural Language Processing",
    ]


def test_empty_candidates_are_ignored():
    text = """
    Python,,React,,,SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


# ============================================================
# Formatting
# ============================================================

def test_case_variation_preserves_surface_form():
    text = """
    python
    PYTHON
    Python
    """

    result = extract_skills(text)

    assert result["known"] == [
        "python",
    ]


def test_realistic_mixed_skill_formatting():
    text = """
    Programming Languages: Python, JavaScript
    Frameworks: ReactJS, Express.JS
    Databases: PostgreSQL, MongoDB
    """

    result = extract_skills(text)

    assert "Python" in result["known"]
    assert "JavaScript" in result["known"]
    assert "ReactJS" in result["known"]
    assert "Express.JS" in result["known"]

    assert "PostgreSQL" in result["unknown"]
    assert "MongoDB" in result["unknown"]


# ============================================================
# Real resume regression
# ============================================================

def test_real_resume_skills():
    text = """
    Python
    C++
    SQL
    React
    Express.js
    Next.js
    """

    result = extract_skills(text)

    assert "Python" in result["known"]
    assert "C++" in result["known"]
    assert "SQL" in result["known"]
    assert "React" in result["known"]
    assert "Express.js" in result["known"]
    assert "Next.js" in result["known"]