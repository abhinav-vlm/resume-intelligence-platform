from pathlib import Path
from src.parsers.skills_parser import extract_skills

def test_real_resume_skills():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = extract_skills(text)

    assert result is not None
    assert "Python" in result
    assert "ReactJS" in result