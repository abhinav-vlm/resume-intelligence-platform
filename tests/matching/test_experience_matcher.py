from src.matching.experience_matcher import match_experience

def test_match_experience_meets():
    jd_experience = 3
    resume_experience = 4
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == -1
    assert result['status'] == "meets"

def test_match_experience_underqulified():
    jd_experience = 5
    resume_experience = 4
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == 1
    assert result['status'] == "underqualified"

def test_match_experience_perfect_meet():
    jd_experience = 4
    resume_experience = 4
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] == 0
    assert result['status'] == "meets"

def test_match_experience_jd_null():
    jd_experience = None
    resume_experience = 4
     
    result = match_experience(resume_experience,jd_experience)
    assert result['difference'] is None
    assert result['status'] == "unknown"

def test_match_experience_resume_null():
    jd_experience = 5
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