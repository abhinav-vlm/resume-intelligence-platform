from src.normalizers.education_normalizer import normalize_education

def test_normalize_education_score():
    education = [
        {
            "institution": "NIT Agartala",
            "duration": "2020 – 2024",
            "degree": "Bachelor of Technology",
            "cgpa": "CGPA: 8.30",
        }
    ]

    result = normalize_education(education)

    assert result[0]["score"] == 8.3
    assert result[0]["score_type"] == "CGPA"

def test_normalize_education_percentage():
    education = [
        {
            "institution": "School",
            "duration": "2019 – 2020",
            "degree": "Senior Secondary",
            "cgpa": "Percentage: 73",
        }
    ]

    result = normalize_education(education)

    assert result[0]["score"] == 73.0
    assert result[0]["score_type"] == "percentage"