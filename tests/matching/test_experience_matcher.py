from src.matching.experience_matcher import match_experience,match_skill_experience

def test_match_experience_meets():
    jd_experience = 36
    resume_experience = 48
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == -12
    assert result['status'] == "meets"

def test_match_experience_underqualified():
    jd_experience = 60
    resume_experience = 48
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == 12
    assert result['status'] == "underqualified"

def test_match_experience_perfect_meet():
    jd_experience = 48
    resume_experience = 48
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == 0
    assert result['status'] == "meets"

def test_match_experience_jd_null():
    jd_experience = None
    resume_experience = 48
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] is None
    assert result['status'] == "unknown"

def test_match_experience_resume_null():
    jd_experience = 60
    resume_experience = None
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] is None
    assert result['status'] == "unknown"

def test_match_experience_jd_resume_null():
    jd_experience = None
    resume_experience = None
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] is None
    assert result['status'] == "unknown"

def test_match_experience_jd_resume_0():
    jd_experience = 0
    resume_experience = 0
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == 0
    assert result['status'] == "meets"

def test_skill_experience_underqualified():
    jd = [
        {
            "skill": "Python",
            "experience_months": 36
        }
    ]

    resume = {
        "Python": {
            "intervals": [
                ((2021, 1), (2023, 3))
            ],
            "experience_months": 27
        }
    }

    result = match_skill_experience(resume,jd)

    assert result == [
        {
            "skill": "Python",
            "required_experience_months": 36,
            "candidate_experience_months": 27,
            "difference_months": 9,
            "status": "underqualified"
        }
    ]

def test_skill_experience_exact_match():
    jd = [
        {
            "skill": "Python",
            "experience_months": 36
        }
    ]

    resume = {
        "Python": {
            "intervals": [
                ((2021, 1), (2023, 12))
            ],
            "experience_months": 36
        }
    }

    result = match_skill_experience(resume,jd)

    assert result == [
        {
            "skill": "Python",
            "required_experience_months": 36,
            "candidate_experience_months": 36,
            "difference_months": 0,
            "status": "meets"
        }
    ]

def test_skill_experience_exceeds_requirement():
    jd = [
        {
            "skill": "Python",
            "experience_months": 36
        }
    ]

    resume = {
        "Python": {
            "intervals": [
                ((2021, 1), (2024, 12))
            ],
            "experience_months": 48
        }
    }

    result = match_skill_experience(resume,jd)

    assert result == [
        {
            "skill": "Python",
            "required_experience_months": 36,
            "candidate_experience_months": 48,
            "difference_months": -12,
            "status": "meets"
        }
    ]

def test_skill_experience_missing_candidate_skill():
    jd = [
        {
            "skill": "Python",
            "experience_months": 36
        }
    ]

    resume = {
        "React": {
            "intervals": [
                ((2021, 1), (2024, 12))
            ],
            "experience_months": 48
        }
    }

    result = match_skill_experience(resume,jd)

    assert result == [
        {
            "skill": "Python",
            "required_experience_months": 36,
            "candidate_experience_months": None,
            "difference_months": None,
            "status": "unknown"
        }
    ]
    
def test_skill_experience_multiple_skills():
    jd = [
        {
            "skill": "Python",
            "experience_months": 36
        },
        {
            "skill": "SQL",
            "experience_months": 24
        }
    ]

    resume = {
        "Python": {
            "intervals": [
                ((2021, 1), (2024, 12))
            ],
            "experience_months": 48
        },
        "SQL": {
            "intervals": [
                ((2021, 1), (2024, 12))
            ],
            "experience_months": 48
        }
    }

    result = match_skill_experience(resume,jd)

    assert result == [
        {
            "skill": "Python",
            "required_experience_months": 36,
            "candidate_experience_months": 48,
            "difference_months": -12,
            "status": "meets"
        },
                {
            "skill": "SQL",
            "required_experience_months": 24,
            "candidate_experience_months": 48,
            "difference_months": -24,
            "status": "meets"
        }
    ]

