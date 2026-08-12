from pathlib import Path
from src.parsers.skills_parser import extract_skills
from src.normalizers.skill_normalizer import normalize_skills

def test_real_resume_skills():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    skills = extract_skills(text)
    result = normalize_skills(skills)

    assert result is not None
    assert "Python" in result
    assert "React" in result