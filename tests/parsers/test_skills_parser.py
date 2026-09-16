from pathlib import Path

from src.parsers.skills_parser import extract_skills
from src.normalizers.skill_normalizer import normalize_skills


def test_real_resume_skills():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = extract_skills(text)

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


def test_long_prose_is_not_skill_candidate():
    text = """
    SKILLS
    Python
    React
    Experienced software engineer with strong experience
    in building scalable applications using Python
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
    ]

    assert result["unknown"] == []

def test_empty_candidates_are_ignored():
    text = """
    SKILLS
    Python,,React,,,SQL
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
        "SQL",
    ]

    assert result["unknown"] == []


def test_case_variation_preserves_surface_form():
    text = """
    SKILLS
    python
    REACT
    """

    result = extract_skills(text)

    assert result["known"] == [
        "python",
        "REACT",
    ]


def test_unknown_duplicates_are_deduplicated():
    text = """
    SKILLS
    MongoDB
    mongodb
    MONGODB
    """

    result = extract_skills(text)

    assert result["unknown"] == [
        "MongoDB",
    ]


def test_multi_word_unknown_skill_is_preserved():
    text = """
    SKILLS
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
    SKILLS
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


def test_skills_section_stops_at_next_section():
    text = """
    SKILLS
    Python
    React

    EXPERIENCE
    MongoDB
    PyTorch
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "React",
    ]

    assert result["unknown"] == []

def test_legitimate_long_skill_is_preserved():
    text = """
    SKILLS
    Object Oriented Programming
    Natural Language Processing
    """

    result = extract_skills(text)

    assert result["unknown"] == [
        "Object Oriented Programming",
        "Natural Language Processing",
    ]

def test_known_skills_are_normalized_after_extraction():
    text = """
    SKILLS
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

def test_unknown_skills_are_not_normalized():
    text = """
    SKILLS
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

def test_skills_are_extracted_only_from_skills_section():
    text = """
    SKILLS
    Python
    ReactJS

    EXPERIENCE
    Built applications using MongoDB and Redis.

    PROJECTS
    Used PyTorch and LangChain for experimentation.
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "ReactJS",
    ]

    assert result["unknown"] == []

def test_realistic_mixed_skill_formatting():
    text = """
    TECHNICAL SKILLS:

    Languages: Python, C++, JavaScript
    Frameworks: ReactJS, FastAPI
    Databases: MongoDB, Redis
    Machine Learning: Deep Learning, NLP
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "C++",
        "JavaScript",
        "ReactJS",
        "FastAPI",
    ]

    assert result["unknown"] == [
        "MongoDB",
        "Redis",
        "Deep Learning",
        "NLP",
    ]

def test_pipe_separated_skills():
    text = """
    TECHNICAL SKILLS

    Programming Languages
    Python | C++ | JavaScript

    Frameworks
    ReactJS | FastAPI
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "C++",
        "JavaScript",
        "ReactJS",
        "FastAPI",
    ]

    assert result["unknown"] == []
