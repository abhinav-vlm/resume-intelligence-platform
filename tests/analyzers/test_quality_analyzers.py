from src.analyzers.quality_analyzer import (
    analyze_quality,
    _analyze_education_structure,
    _analyze_experience_structure,
    _analyze_projects_structure,
    _analyze_skills_structure,
)

def test_education_structure_complete():
    education = [
        {
            "institution": "NIT Agartala",
            "degree": "B.Tech",
            "field": "ECE",
            "start_year": 2020,
            "end_year": 2024,
            "score": 8.3,
            "score_type": "CGPA",
        }
    ]

    result = _analyze_education_structure(education)

    assert result == [
        {
            "index": 0,
            "issues": [],
        }
    ]

def test_education_structure_missing_degree():
    education = [
        {
            "institution": "NIT Agartala",
            "degree": None,
            "field": "ECE",
            "start_year": 2020,
            "end_year": 2024,
            "score": 8.3,
            "score_type": "CGPA",
        }
    ]

    result = _analyze_education_structure(education)

    assert result[0]["issues"] == [
        "missing_degree"
    ]

def test_education_structure_multiple_missing_fields():
    education = [
        {
            "institution": None,
            "degree": None,
            "field": "ECE",
            "start_year": None,
            "end_year": 2024,
            "score": None,
            "score_type": None,
        }
    ]

    result = _analyze_education_structure(education)

    assert result[0]["issues"] == [
        "missing_institution",
        "missing_degree",
        "missing_start_year",
    ]

def test_experience_structure_complete():
    experience = [
        {
            "company": "Gosotek",
            "position": "Software Engineer",
            "start_month": "January",
            "end_month": "February",
            "start_year": 2024,
            "end_year": 2024,
            "employment_type": "intern",
            "description": [
                "• Built something useful."
            ],
        }
    ]

    result = _analyze_experience_structure(experience)

    assert result == [
        {
            "index": 0,
            "issues": [],
        }
    ]


def test_experience_structure_missing_fields():
    experience = [
        {
            "company": None,
            "position": None,
            "start_year": None,
            "end_year": None,
            "description": None,
        }
    ]

    result = _analyze_experience_structure(experience)

    assert result[0]["issues"] == [
        "missing_company",
        "missing_position",
        "missing_start_year",
        "missing_end_year",
        "missing_description",
    ]

def test_project_structure_complete():
    projects = [
        {
            "project": "Resume Parser",
            "metadata": [],
            "description": [
                "• Built a resume parsing system."
            ],
        }
    ]

    result = _analyze_projects_structure(projects)

    assert result == [
        {
            "index": 0,
            "issues": [],
        }
    ]

def test_project_structure_missing_fields():
    projects = [
        {
            "project": None,
            "metadata": [],
            "description": None,
        }
    ]

    result = _analyze_projects_structure(projects)

    assert result[0]["issues"] == [
        "missing_project",
        "missing_description",
    ]

def test_skills_structure_complete():
    skills = [
        "Python",
        "SQL",
        "FastAPI",
    ]

    result = _analyze_skills_structure(skills)

    assert result == []

def test_skills_structure_missing():
    skills = []

    result = _analyze_skills_structure(skills)

    assert result == [
        {
            "issue": "missing_skills"
        }
    ]

def test_analyze_structure():
    resume = {
        "education": [],
        "experience": [],
        "projects": [],
        "skills": ["Python"],
    }

    result = analyze_quality(resume)

    assert result["structure"]["education"] == []
    assert result["structure"]["experience"] == []
    assert result["structure"]["projects"] == []
    assert result["structure"]["skills"] == []