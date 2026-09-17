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
    ],
)
def test_is_section_header_accepts_known_headers(line):
    assert is_section_header(line.strip().lower())


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
    assert not is_section_header(line.strip().lower())


# ============================================================
# Basic boundary behavior
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
    assert "Python" in result[0]["text"]
    assert "SQL" in result[0]["text"]

    assert result[1]["name"] == "experience"
    assert "ML Engineer" in result[1]["text"]


def test_section_header_is_not_added_to_section_text():
    text = """SKILLS
Python
EXPERIENCE
ML Engineer"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == "Python"
    assert result[1]["text"].strip() == "ML Engineer"


# ============================================================
# Content preservation
# ============================================================

def test_content_preserves_original_case():
    text = """SKILLS
Python
TensorFlow
XGBoost"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == "Python\nTensorFlow\nXGBoost"


def test_content_preserves_line_boundaries():
    text = """SKILLS
Python
SQL
Docker"""

    result = detect_sections(text)

    assert result[0]["text"].strip().splitlines() == [
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

    assert result[0]["name"] == "experience"
    assert "Experience with Python and SQL" in result[0]["text"]
    assert "Developed skills in ML systems" in result[0]["text"]


# ============================================================
# Whitespace / formatting attacks
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


def test_blank_lines_inside_section_do_not_create_new_section():
    text = """SKILLS
Python

SQL

Docker"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"

    lines = result[0]["text"].splitlines()

    assert "Python" in lines
    assert "SQL" in lines
    assert "Docker" in lines


# ============================================================
# Boundary attacks
# ============================================================

def test_consecutive_headers_create_empty_previous_section():
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


def test_repeated_same_header_creates_separate_boundaries():
    text = """SKILLS
Python
SKILLS
SQL"""

    result = detect_sections

# ============================================================
# Block 4: Hardened / Adversarial Boundary Tests
# ============================================================


def test_header_with_colon_is_recognized():
    text = """SKILLS:
Python
SQL
EXPERIENCE:
ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
    assert "Python" in result[0]["text"]
    assert result[1]["name"] == "experience"
    assert "ML Engineer" in result[1]["text"]


def test_technical_skills_colon_variant_is_recognized():
    text = """TECHNICAL SKILLS :
Python
Docker
AWS"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "technical skills"
    assert "Python" in result[0]["text"]


def test_header_with_multiple_spaces_is_normalized():
    text = """   TECHNICAL   SKILLS
Python
Docker"""

    result = detect_sections(text)

    # This should currently fail unless the detector/config
    # explicitly supports internal whitespace normalization.
    assert result[0]["name"] == "technical skills"


def test_header_with_tabs_between_words():
    text = """TECHNICAL\tSKILLS
Python
Docker"""

    result = detect_sections(text)

    # Hardened requirement:
    # formatting whitespace should not change the section identity.
    assert result[0]["name"] == "technical skills"


def test_unicode_non_breaking_space_in_header():
    text = "TECHNICAL\u00a0SKILLS\nPython\nDocker"

    result = detect_sections(text)

    assert result[0]["name"] == "technical skills"


def test_header_surrounded_by_blank_lines():
    text = """SKILLS


Python
SQL


EXPERIENCE


ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
    assert result[1]["name"] == "experience"

    assert "Python" in result[0]["text"]
    assert "SQL" in result[0]["text"]
    assert "ML Engineer" in result[1]["text"]


def test_resume_ending_immediately_after_header():
    text = """SKILLS
Python
EXPERIENCE"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
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
    text = "SKILLS"

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == ""


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


def test_header_word_inside_long_sentence_is_not_boundary():
    text = """EXPERIENCE
Experience working with distributed systems
Skills include Python and SQL
Projects include NLP systems"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "experience"

    assert "Experience working with distributed systems" in result[0]["text"]
    assert "Skills include Python and SQL" in result[0]["text"]
    assert "Projects include NLP systems" in result[0]["text"]


def test_section_header_with_trailing_spaces_preserves_content():
    text = """SKILLS    
Python
SQL"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == "Python\nSQL"


def test_empty_lines_do_not_create_empty_sections():
    text = """SKILLS



EXPERIENCE



PROJECTS"""

    result = detect_sections(text)

    assert len(result) == 3
    assert [section["name"] for section in result] == [
        "skills",
        "experience",
        "projects",
    ]


def test_mixed_case_headers_produce_canonical_names():
    text = """sKiLlS
Python
pRoJeCtS
Resume Parser"""

    result = detect_sections(text)

    assert len(result) == 2
    assert result[0]["name"] == "skills"
    assert result[1]["name"] == "projects"


def test_content_case_is_not_destroyed_by_header_normalization():
    text = """SKILLS
Python
TensorFlow
XGBoost
AWS"""

    result = detect_sections(text)

    assert result[0]["text"].strip() == (
        "Python\n"
        "TensorFlow\n"
        "XGBoost\n"
        "AWS"
    )


def test_resume_with_many_section_transitions():
    text = """SUMMARY
ML Engineer

SKILLS
Python
PyTorch

EXPERIENCE
Company A
Built models

PROJECTS
Resume Intelligence Platform

EDUCATION
B.Tech

CERTIFICATIONS
AWS Certified"""

    result = detect_sections(text)

    assert [section["name"] for section in result] == [
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications",
    ]


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


def test_leading_blank_lines_do_not_create_section():
    text = """


SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert "Python" in result[0]["text"]


def test_trailing_blank_lines_do_not_create_section():
    text = """SKILLS
Python


"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == "Python"

# ============================================================
# Block 5: Boundary Contract Completion
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
    assert result[0]["text"].strip() == (
        "John Doe\n"
        "Machine Learning Engineer\n"
        "john@example.com\n"
        "+91 9876543210"
    )

    assert result[1]["name"] == "skills"
    assert result[1]["text"].strip() == "Python\nSQL"


def test_preamble_is_not_merged_into_first_section():
    text = """John Doe
ML Engineer

EXPERIENCE
ML Engineer at Company A"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "preamble"
    assert "John Doe" in result[0]["text"]
    assert "ML Engineer" in result[0]["text"]

    assert result[1]["name"] == "experience"
    assert "John Doe" not in result[1]["text"]


def test_preamble_with_blank_lines_is_preserved():
    text = """John Doe

ML Engineer

Bangalore


SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 2

    assert result[0]["name"] == "preamble"
    assert "John Doe" in result[0]["text"]
    assert "ML Engineer" in result[0]["text"]
    assert "Bangalore" in result[0]["text"]

    assert result[1]["name"] == "skills"


def test_resume_with_no_sections_returns_preamble():
    text = """John Doe
Machine Learning Engineer
Python Developer
Bangalore"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "preamble"

    assert result[0]["text"].strip() == (
        "John Doe\n"
        "Machine Learning Engineer\n"
        "Python Developer\n"
        "Bangalore"
    )


def test_empty_text_returns_no_sections():
    result = detect_sections("")

    assert result == []


def test_whitespace_only_text_returns_no_sections():
    text = "   \n\t\n   \n"

    result = detect_sections(text)

    assert result == []


def test_only_blank_lines_before_section_do_not_create_preamble():
    text = """


SKILLS
Python"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "skills"
    assert result[0]["text"].strip() == "Python"


def test_sectionless_resume_preserves_original_content():
    text = """John Doe
ML Engineer

Python
TensorFlow
Docker"""

    result = detect_sections(text)

    assert len(result) == 1
    assert result[0]["name"] == "preamble"

    assert "John Doe" in result[0]["text"]
    assert "ML Engineer" in result[0]["text"]
    assert "Python" in result[0]["text"]
    assert "TensorFlow" in result[0]["text"]
    assert "Docker" in result[0]["text"]


def test_preamble_content_preserves_original_case():
    text = """John DOE
Machine Learning Engineer
Python Developer

SKILLS
Python"""

    result = detect_sections(text)

    assert result[0]["name"] == "preamble"

    assert "John DOE" in result[0]["text"]
    assert "Machine Learning Engineer" in result[0]["text"]
    assert "Python Developer" in result[0]["text"]


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

    assert "john@example.com" in result[0]["text"]
    assert "Python" in result[1]["text"]
    assert "ML Engineer" in result[2]["text"]
    assert "B.Tech" in result[3]["text"]


def test_contact_like_lines_inside_sections_remain_section_content():
    text = """SKILLS
Python
john@example.com
+91 9876543210

EXPERIENCE
ML Engineer"""

    result = detect_sections(text)

    assert len(result) == 2

    assert "john@example.com" in result[0]["text"]
    assert "+91 9876543210" in result[0]["text"]

    assert "john@example.com" not in result[1]["text"]