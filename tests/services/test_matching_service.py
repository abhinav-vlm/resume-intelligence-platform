from src.services.matching_service import calculate_match


def test_calculate_match():

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
    "experience": [
        {
            "position": "Machine Learning Engineer"
        }
    ],
}

    jd_data = {
        "role": "ML Engineer",
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

    result = calculate_match(resume_data, jd_data)

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
    assert result["role_match"]["candidate_roles"] == [
    "Machine Learning Engineer"]   
    assert result["role_match"]["target_role"] == "ML Engineer"
    assert result["role_match"]["canonical_candidate_roles"] == [
    "machine learning engineer"]
    assert result["role_match"]["canonical_target_role"] == (
    "machine learning engineer")
    assert result["role_match"]["status"] == "match"