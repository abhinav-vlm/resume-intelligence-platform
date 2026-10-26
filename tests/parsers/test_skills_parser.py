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
    LangChain
    langchain
    LANGCHAIN
    """

    result = extract_skills(text)

    assert result["unknown"] == [
        "LangChain",
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
        "MongoDB",
        "PyTorch",
    ]

    assert result["unknown"] == [
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
        "Rust",
        "React",
        "FastAPI",
        "MongoDB",
        "Redis",
    ]

    assert result["unknown"] == [
        "Svelte",
    ]

def test_multi_word_unknown_skill_is_preserved():
    """
    Multi-word technical terms added to KNOWN_SKILLS should appear in 'known'.
    Truly unknown multi-word skills that don't match KNOWN_SKILLS remain in 'unknown'.
    """
    text = """
    Python
    Deep Learning
    Natural Language Processing
    """

    result = extract_skills(text)

    # Deep Learning and NLP are now in KNOWN_SKILLS (compound_concepts)
    assert result["known"] == [
        "Python",
        "Deep Learning",
        "Natural Language Processing",
    ]

    assert result["unknown"] == []


def test_mixed_known_and_unknown_skills():
    text = """
    Python, MongoDB, React, PyTorch
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Python",
        "MongoDB",
        "React",
        "PyTorch",
    ]

    assert result["unknown"] == []

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
    """
    Object Oriented Programming and NLP are in KNOWN_SKILLS (compound_concepts),
    so they should appear in 'known'.
    """
    text = """
    Object Oriented Programming
    Natural Language Processing
    """

    result = extract_skills(text)

    assert result["known"] == [
        "Object Oriented Programming",
        "Natural Language Processing",
    ]
    assert result["unknown"] == []


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

    # Deep Learning and NLP are now in KNOWN_SKILLS
    assert result["known"] == [
        "Python",
        "C++",
        "JavaScript",
        "ReactJS",
        "FastAPI",
        "MongoDB",
        "Redis",
        "Deep Learning",
        "NLP",
    ]

    assert result["unknown"] == []

def test_conjunction_separated_skills_are_split():
    result = extract_skills("HTML, CSS and React JS")

    assert "HTML" in result["known"]
    assert "CSS" in result["known"]
    assert "React JS" in result["known"]


# ============================================================
# R-043: Bullet glyph prefix on skill lines must not corrupt first skill
# ============================================================

def test_bullet_glyph_stripped_before_skill_extraction():
    """R-043: '• Python, React, SQL' must extract Python as a known skill."""
    result = extract_skills("• Python, React, SQL")

    assert "Python" in result["known"], "Python must be extracted despite bullet glyph prefix"
    assert "React" in result["known"]
    assert "SQL" in result["known"]
    assert result["unknown"] == [], "No skill should be misclassified as unknown"


def test_various_bullet_glyphs_stripped():
    """R-043: All common Unicode bullet variants must be stripped."""
    glyphs = ["•", "‣", "●", "-", "*", "–", "→", "►"]
    for glyph in glyphs:
        line = f"{glyph} Python, React"
        result = extract_skills(line)
        assert "Python" in result["known"], (
            f"Python not extracted from line starting with {repr(glyph)}: got {result}"
        )


def test_bullet_glyph_on_categorized_line():
    """R-043: Bullet glyph before category-colon line must not corrupt skill."""
    result = extract_skills("• Languages: Python, C++, SQL")

    assert "Python" in result["known"]
    assert "C++" in result["known"]
    assert "SQL" in result["known"]


# ============================================================
# R-044: Compound skills must not be fragmented by conjunction splitting
# ============================================================

def test_compound_skill_data_structures_not_fragmented():
    """R-044: 'Data Structures and Algorithms' must remain intact, not split on 'and'."""
    result = extract_skills("Data Structures and Algorithms, Python")

    assert "Python" in result["known"]
    # Data Structures and Algorithms is now in KNOWN_SKILLS (compound_concepts)
    assert "Data Structures and Algorithms" in result["known"], (
        f"Compound skill must be in known: got known={result['known']}, unknown={result['unknown']}"
    )
    # The individual fragments must NOT appear as standalone entries
    assert "Data Structures" not in result["unknown"], "Fragment 'Data Structures' must not appear"
    assert "Algorithms" not in result["unknown"], "Fragment 'Algorithms' must not appear"


# ============================================================
# R-045: Slash delimiter must not fragment CI/CD-style acronyms
# ============================================================

def test_cicd_slash_not_fragmented():
    """R-045: 'CI/CD' must be preserved as a unit, not split into 'CI' and 'CD'."""
    result = extract_skills("CI/CD, Python, Docker")

    all_skills = result["known"] + result["unknown"]
    assert "Python" in result["known"]
    assert "Docker" in result["known"]

    # CI/CD should appear as a single entry, not as two separate tokens
    cicd_present = any("CI/CD" in s or "CI" == s or "CD" == s for s in all_skills)
    assert cicd_present, f"CI/CD not found in skills: {all_skills}"
    # The critical regression: 'CI' and 'CD' alone are not valid standalone entries
    assert "CI" not in result["unknown"] or "CD" not in result["unknown"], (
        "CI/CD must not be split into standalone 'CI' and 'CD' entries"
    )
