from src.services.matching_service import match_resume_to_jd


def test_match_resume_to_jd():

    resume_data = {
        "skills": ["Python", "FastAPI", "SQL"],
        "total_experience_months": 36,
        "skill_experience": {
            "Python": {
                "experience_months": 36,
            },
            "FastAPI": {
                "experience_months": 24,
            },
        },
    }

    jd_data = {
        "skills": ["Python", "FastAPI", "Docker"],
        "experience_months": 24,
        "skill_specific_experience": [
            {
                "skill": "Python",
                "experience_months": 24,
            },
            {
                "skill": "FastAPI",
                "experience_months": 12,
            },
        ],
    }

    result = match_resume_to_jd(resume_data, jd_data)

    assert result["skill_match"]["matched"] == [
        "Python",
        "FastAPI",
    ]

    assert result["skill_match"]["unmatched"] == [
        "Docker",
    ]

    assert result["skill_match"]["extra"] == [
        "SQL",
    ]

    assert result["experience_match"]["required"] == 24
    assert result["experience_match"]["candidate"] == 36
    assert result["experience_match"]["difference"] == -12
    assert result["experience_match"]["status"] == "meets"

    assert result["skill_experience_match"][0] == {
        "skill": "Python",
        "required_experience_months": 24,
        "candidate_experience_months": 36,
        "difference_months": -12,
        "status": "meets",
    }

    assert result["skill_experience_match"][1] == {
        "skill": "FastAPI",
        "required_experience_months": 12,
        "candidate_experience_months": 24,
        "difference_months": -12,
        "status": "meets",
    }