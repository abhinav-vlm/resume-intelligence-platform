from src.normalizers.experience_normalizer import normalize_experience,_normalize_duration

def test_normalize_duration_four():
   duration = "January - February, 2024"

   result = _normalize_duration(duration)

   assert result == ("January", "February", 2024, 2024)

def test_normalize_duration_two_month():
   duration = "January 2024"
   
   result = _normalize_duration(duration)
   assert result ==  ("January", None, 2024, None)

def test_normalize_duration_two_year():
   duration = "2022 - 2024"
   result = _normalize_duration(duration)
   assert result ==  (None, None, 2022, 2024)

def test_normalize_duration_one():
   duration = "2024"
   result = _normalize_duration(duration)
   assert result ==  (None, None, 2024, None)

def test_normalize_experience():
   experience = [
    {
        "company": "Gosotek",
        "duration": "January - February, 2024",
        "role": "Front-End Software Engineering (Remote Intern)",
        "description": [
            "• Utilized Latest technology in Next library"
        ]
    }
    ]
   result = normalize_experience(experience)
   assert result[0] == {
        "company": "Gosotek",
        "start_month": "January",
        "end_month": "February",
        "start_year": 2024,
        "end_year": 2024,
        "position": "Front-End Software Engineering (Remote Intern)",
        "description": [
            "• Utilized Latest technology in Next library"
        ]
    }
