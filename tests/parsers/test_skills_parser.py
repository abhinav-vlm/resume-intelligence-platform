from pathlib import Path

from src.parsers.skills_parser import extract_skills
from src.normalizers.skill_normalizer import normalize_skills


def test_real_resume_skills():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = extract_skills(text)

    assert result is not None

    skills = normalize_skills(result["known"])

    assert "Python" in skills
    assert "React" in skills


def test_plain_skill_lines():
    text = """
    SKILLS
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
    SKILLS
    Python, React, SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_categorized_skill_lines():
    text = """
    TECHNICAL SKILLS:
    Languages: Python, C++, SQL
    Frameworks: React, FastAPI
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "C++",
        "SQL",
        "React",
        "FastAPI",
    ]

    assert result["unknown"] == []


def test_duplicate_skills():
    text = """
    SKILLS
    Python, React
    Python, SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_skill_boundary_matching():
    text = """
    SKILLS
    C
    C++
    Java
    JavaScript
    SQL
    MySQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "C",
        "C++",
        "Java",
        "JavaScript",
        "SQL",
        "MySQL",
    ]


def test_skill_aliases_are_extracted():
    text = """
    SKILLS
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

    normalized = normalize_skills(result["known"])

    assert normalized == [
        "React",
        "Express.js",
        "Next.js",
    ]


def test_unknown_skills_are_preserved():
    text = """
    SKILLS
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

def test_unknown_skills_are_preserved():
    text = """
    SKILLS
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
    TECHNICAL SKILLS:
    Languages: Python, C++, Rust
    Frameworks: React, FastAPI, Svelte
    Databases: MongoDB, Redis
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "C++",
        "React",
        "FastAPI",
    ]

    assert result["unknown"] == [
        "Rust",
        "Svelte",
        "MongoDB",
        "Redis",
    ]

