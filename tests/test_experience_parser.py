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