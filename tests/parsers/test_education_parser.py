from pathlib import Path
from src.parsers.education_parser import process_education

def test_real_resume_education():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = process_education(text)

    assert result is not None
    assert len(result) == 3
    assert result[0]["institution"] == "National Institute of Technology, Agartala"