from src.matching.skill_matcher import match_skills

def test_match_skills():
    resume = ["Python", "FastAPI", "AWS", "TensorFlow"]

    jd = ["Python", "FastAPI", "Kubernetes", "AWS", "PyTorch"]
     
    result = match_skills(resume,jd)
    assert result['matched'] == ["Python", "FastAPI", "AWS"]
    assert result['unmatched'] == ["Kubernetes", "PyTorch"]
    assert result['extra'] == ["TensorFlow"]

def test_match_skills_empty_resume():
    resume = []

    jd = ["Python", "FastAPI", "Kubernetes", "AWS", "PyTorch"]
     
    result = match_skills(resume,jd)
    assert result['matched'] == []
    assert result['unmatched'] == ["Python", "FastAPI", "Kubernetes", "AWS", "PyTorch"]
    assert result['extra'] == []

def test_match_skills_empty_resume_jd():
    resume = []

    jd = []
     
    result = match_skills(resume,jd)
    assert result['matched'] == []
    assert result['unmatched'] == []
    assert result['extra'] == []

def test_match_skills_empty_jd():
    resume = ["Python", "FastAPI", "Kubernetes", "AWS", "PyTorch"]

    jd = []
     
    result = match_skills(resume,jd)
    assert result['matched'] == []
    assert result['unmatched'] == []
    assert result['extra'] == ["Python", "FastAPI", "Kubernetes", "AWS", "PyTorch"]
