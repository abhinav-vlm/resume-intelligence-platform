import pytest

from src.parsers.section_detector import detect_sections, is_section_header


# ============================================================
# is_section_header()
# ============================================================

@pytest.mark.parametrize(
    "line",
    [
        "SKILLS",
        "skills",
        "Skills",
        "  SKILLS  ",
        "\tSkills\t",
        "Professional Experience",
        " professional experience ",
        "EDUCATION",
        "Projects",
        "Technical Skills:",
        "TECHNICAL   SKILLS",
        "TECHNICAL\tSKILLS",
    ],
)
def test_is_section_header_accepts_known_headers(line):
    assert is_section_header(line)


@pytest.mark.parametrize(
    "line",
    [
        "",
        " ",
        "\t",
        "Python",
        "Python skills include TensorFlow",
        "Experience with Python",
        "Education: B.Tech",
        "Projects completed",
        "My Skills",
        "Technical Skills: Python, SQL",
    ],
)
def test_is_section_header_rejects_non_headers(line):
    assert not is_section_header(line)


# ============================================================
# Basic section boundaries
# ============================================================

def test_detect_sections_does_not_merge_two_sections():
    text = """SKILLS
Python
SQL
EXPERIENCE
ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "skills"
    assert result[0]["original_name"] == "skills"
    assert "Python" in result[0]["text"]
    assert "SQL" in result[0]["text"]

    assert result[1]["name"] == "experience"
    assert result[1]["original_name"] == "experience"
    assert "ML Engineer" in result[1]["text"]


def test_section_header_is_not_added_to_section_text():
    text = """SKILLS
Python
EXPERIENCE
ML Engineer"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == "Python"
    assert result[1]["text"].strip() == "ML Engineer"


def test_section_content_does_not_leak_between_boundaries():
    text = """SKILLS
Python
SQL
EXPERIENCE
Company A
PROJECTS
Project A"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == "Python\nSQL"
    assert result[1]["text"].strip() == "Company A"
    assert result[2]["text"].strip() == "Project A"


# ============================================================
# Canonical section names
# ============================================================

@pytest.mark.parametrize(
    "header,canonical",
    [
        ("SKILLS", "skills"),
        ("Technical Skills", "skills"),
        ("TECHNICAL SKILLS:", "skills"),
        ("Education", "education"),
        ("Professional Experience", "experience"),
        ("Work Experience", "experience"),
    ],
)
def test_section_headers_are_canonicalized(header, canonical):
    result = detect_sections(f"{header}\nContent")

    assert len(result) == 1
    assert result[0]["name"] == canonical


@pytest.mark.parametrize(
    "header,expected_original",
    [
        ("SKILLS", "skills"),
        ("Technical Skills", "technical skills"),
        ("TECHNICAL SKILLS:", "technical skills"),
        ("technical   skills", "technical skills"),
        ("TECHNICAL\tSKILLS", "technical skills"),
    ],
)
def test_original_section_name_is_preserved(header, expected_original):
    result = detect_sections(f"{header}\nPython")

    assert len(result) == 1
    assert result[0]["original_name"] == expected_original
    
def test_canonical_name_and_original_name_are_distinct():
    text = """TECHNICAL SKILLS
Python
SQL"""

    result = detect_sections(text)

    assert result[0]["name"] == "skills"
    assert result[0]["original_name"] == "technical skills"


# ============================================================
# Multiple sections with same canonical name
# ============================================================

def test_multiple_skill_aliases_remain_separate_sections():
    text = """TECHNICAL SKILLS
Python
SQL

NON TECHNICAL SKILLS
Communication
Leadership"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "skills"
    assert result[0]["original_name"] == "technical skills"
    assert "Python" in result[0]["text"]

    assert result[1]["name"] == "skills"
    assert result[1]["original_name"] == "non technical skills"
    assert "Communication" in result[1]["text"]


def test_duplicate_sections_do_not_merge():
    text = """SKILLS
Python

EXPERIENCE
Company A

SKILLS
SQL"""

    result = detect_sections(text)

    assert len(result) == 3

    assert result[0]["name"] == "skills"
    assert "Python" in result[0]["text"]

    assert result[1]["name"] == "experience"
    assert "Company A" in result[1]["text"]

    assert result[2]["name"] == "skills"
    assert "SQL" in result[2]["text"]


# ============================================================
# Preamble
# ============================================================

def test_preamble_before_first_section_is_preserved():
    text = """John Doe
Machine Learning Engineer
john@example.com
+91 9876543210

SKILLS
Python
SQL"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "preamble"
    assert result[0]["original_name"] is None

    assert result[0]["text"].strip() == (
        "John Doe\n"
        "Machine Learning Engineer\n"
        "john@example.com\n"
        "+91 9876543210"
    )

    assert result[1]["name"] == "skills"


def test_preamble_does_not_interfere_with_section_boundaries():
    text = """John Doe
ML Engineer
john@example.com

SKILLS
Python
SQL

EXPERIENCE
ML Engineer

EDUCATION
B.Tech"""

    result = detect_sections(text)

    assert [section["name"] for section in result] == [
        "preamble",
        "skills",
        "experience",
        "education",
    ]


def test_only_blank_lines_before_section_do_not_create_preamble():
    text = """


SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"


def test_resume_with_no_sections_returns_preamble():
    text = """John Doe
Machine Learning Engineer
Python Developer
Bangalore"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "preamble"
    assert result[0]["original_name"] is None


# ============================================================
# Empty / boundary sections
# ============================================================

def test_consecutive_headers_create_empty_sections():
    text = """SKILLS
EXPERIENCE
PROJECTS"""

    result = detect_sections(text)

    assert len(result) == 3

    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == ""

    assert result[1]["name"] == "experience"
    assert result[1]["text"].strip() == ""

    assert result[2]["name"] == "projects"
    assert result[2]["text"].strip() == ""


def test_resume_ending_immediately_after_header():
    text = """SKILLS
Python
EXPERIENCE"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["text"].strip() == "Python"
    assert result[1]["name"] == "experience"
    assert result[1]["text"].strip() == ""


def test_resume_starting_with_header():
    text = """SKILLS
Python
SQL"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == "Python\nSQL"


def test_resume_with_only_a_header():
    result = detect_sections("SKILLS")

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == ""


# ============================================================
# Content preservation
# ============================================================

def test_content_preserves_original_case():
    text = """SKILLS
Python
TensorFlow
XGBoost"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == (
        "Python\nTensorFlow\nXGBoost"
    )


def test_content_preserves_line_boundaries():
    text = """SKILLS
Python
SQL
Docker"""

    result = detect_sections(text)

    assert result[0]["text"].splitlines() == [
        "Python",
        "SQL",
        "Docker",
    ]


def test_content_containing_header_words_is_not_split():
    text = """EXPERIENCE
Experience with Python and SQL
Developed skills in ML systems
SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 2
    assert "Experience with Python and SQL" in result[0]["text"]
    assert "Developed skills in ML systems" in result[0]["text"]


def test_unknown_header_does_not_steal_content():
    text = """EXPERIENCE
Software Engineer
CAREER HISTORY
Built ML pipelines
SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "experience"
    assert "CAREER HISTORY" in result[0]["text"]
    assert "Built ML pipelines" in result[0]["text"]

    assert result[1]["name"] == "skills"


# ============================================================
# Whitespace / formatting
# ============================================================

def test_header_with_surrounding_whitespace_is_detected():
    text = """   SKILLS
Python
   EXPERIENCE
ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
    assert result[1]["name"] == "experience"


def test_header_with_colon_is_recognized():
    text = """SKILLS:
Python
SQL
EXPERIENCE:
ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
    assert result[1]["name"] == "experience"


def test_header_with_multiple_spaces_is_normalized():
    text = """TECHNICAL   SKILLS
Python
Docker"""

    result = detect_sections(text)

    assert result[0]["name"] == "skills"
    assert result[0]["original_name"] == "technical skills"


def test_header_with_tabs_is_normalized():
    text = """TECHNICAL\tSKILLS
Python
Docker"""

    result = detect_sections(text)

    assert result[0]["name"] == "skills"
    assert result[0]["original_name"] == "technical skills"


def test_unicode_non_breaking_space_is_normalized():
    text = "TECHNICAL\u00a0SKILLS\nPython\nDocker"

    result = detect_sections(text)

    assert result[0]["name"] == "skills"


def test_blank_lines_inside_section_do_not_create_sections():
    text = """SKILLS
Python

SQL

Docker"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"


# ============================================================
# Empty input
# ============================================================

def test_empty_text_returns_no_sections():
    assert detect_sections("") == []


def test_whitespace_only_text_returns_no_sections():
    text = "   \n\t\n   \n"

    assert detect_sections(text) == []