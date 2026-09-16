from pathlib import Path
from src.parsers.experience_parser import process_experience

def test_real_resume_experience():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = process_experience(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["company"] == "Gosotek"

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