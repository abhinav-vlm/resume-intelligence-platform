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

def test_process_education_accepts_isolated_section_text():
    text = """
    Bachelor of Technology
    National Institute of Technology, Agartala
    Computer Science
    2020 - 2024
    """

    result = process_education(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["institution"] == "National Institute of Technology, Agartala"
    
def test_process_education_parses_multiple_education_entries():
    text = """
    Bachelor of Technology
    Computer Science
    National Institute of Technology
    2020 - 2024

    Master of Science
    Data Science
    ABC University
    2024 - 2026
    """

    result = process_education(text)

    assert result is not None
    assert len(result) == 2