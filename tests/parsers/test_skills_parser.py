from src.parsers.skills_parser import extract_skills


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


def test_categorized_skill_lines():
    text = """
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


def test_pipe_separated_skills():
    text = """
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


# ============================================================
# Deduplication
# ============================================================

def test_duplicate_skills():
    text = """
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
# Boundary matching
# ============================================================

def test_skill_boundary_matching():
    text = """
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


# ============================================================
# Alias extraction
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


# ============================================================
# Candidate validation
# ============================================================

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


# ============================================================
# Case handling
# ============================================================

def test_case_variation_preserves_surface_form():
    text = """
    python
    REACT
    """

    result = extract_skills(text)

    assert result["known"] == [
        "python",
        "REACT",
    ]


# ============================================================
# Realistic mixed formatting
# ============================================================

def test_realistic_mixed_skill_formatting():
    text = """
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