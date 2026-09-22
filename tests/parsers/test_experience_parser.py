from pathlib import Path

from src.parsers.section_detector import detect_sections
from src.parsers.experience_parser import (
    process_experience,
    _extract_experience,
)


def test_real_resume_experience():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    sections = detect_sections(text)

    experience_text = "\n".join(
        section["text"]
        for section in sections
        if section["name"] == "experience"
    )

    result = process_experience(experience_text)

    assert result is not None
    assert len(result) == 1


def test_wrapped_experience_bullet_is_preserved():
    text = """
    EXPERIENCE

    Software Engineer
    ABC Technologies
    Jan 2024 - Present

    • Built REST APIs that reduced page loading
      10 percent through caching.
    """

    result = process_experience(text)

    assert result is not None
    assert len(result) == 1

    assert result[0]["company"] == "ABC Technologies"
    assert result[0]["role"] == "Software Engineer"
    assert result[0]["duration"] == "Jan 2024 - Present"

    assert result[0]["description"] == [
        "• Built REST APIs that reduced page loading 10 percent through caching."
    ]


def test_multiple_wrapped_experience_bullets_are_preserved():
    text = """
    EXPERIENCE

    Software Engineer
    ABC Technologies
    Jan 2024 - Present

    • Built REST APIs that reduced page loading
      10 percent through caching.

    • Developed authentication services using JWT
      and OAuth.

    • Improved database query performance by
      optimizing SQL indexes.
    """

    result = process_experience(text)

    assert result is not None
    assert len(result) == 1

    assert result[0]["description"] == [
        "• Built REST APIs that reduced page loading 10 percent through caching.",
        "• Developed authentication services using JWT and OAuth.",
        "• Improved database query performance by optimizing SQL indexes.",
    ]


def test_process_experience_accepts_isolated_experience_section():
    text = """
    Software Engineer
    ABC Technologies
    Jan 2023 - Dec 2024
    Built machine learning applications.
    """

    result = process_experience(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["company"] == "ABC Technologies"
    assert result[0]["duration"] == "Jan 2023 - Dec 2024"


def test_process_experience_parses_multiple_experiences():
    text = """
    Software Engineer
    ABC Technologies
    Jan 2023 - Dec 2024
    Built machine learning applications.

    Data Analyst
    XYZ Corporation
    Jan 2021 - Dec 2022
    Developed analytics dashboards.
    """

    result = process_experience(text)

    assert result is not None
    assert len(result) == 2


def test_process_experience_does_not_apply_top_level_section_boundaries():
    text = """
    Software Engineer
    ABC Technologies
    Jan 2023 - Dec 2024
    Built machine learning applications.

    Projects
    Internal ML Platform
    """

    result = process_experience(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["company"] == "ABC Technologies"


def test_isolated_experience_extraction_shape():
    text = """
    Software Engineer
    ABC Technologies
    Jan 2023 - Dec 2024
    Built machine learning applications.
    """

    blocks = _extract_experience(text)

    assert blocks is not None
    assert len(blocks) == 1
