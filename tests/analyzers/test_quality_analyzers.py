from src.analyzers.quality_analyzer import (
    analyze_quality,
    _analyze_education_structure,
    _analyze_experience_structure,
    _analyze_projects_structure,
    _analyze_skills_structure,
    _analyze_experience_content,
    _analyze_projects_content,
    _has_metrics,_analyze_education_consistency
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


def test_experience_content():
    experience = [
        {
            "description": [
                "Built REST API",
                "Improved latency by 30%",
            ]
        }
    ]

    result = _analyze_experience_content(experience)

    assert result == [
        {
            "index": 0,
            "bullet_count": 2,
            "content_length": (
                len("Built REST API")
                + len("Improved latency by 30%")
            ),
            "has_metrics": True,
        }
    ]


def test_experience_content_without_description():
    experience = [
        {}
    ]

    result = _analyze_experience_content(experience)

    assert result == [
        {
            "index": 0,
            "bullet_count": 0,
            "content_length": 0,
            "has_metrics": False,
        }
    ]


def test_project_content():
    projects = [
        {
            "description": [
                "Built a scalable API",
                "Improved response time by 40%",
                "Handled 10,000 users",
            ]
        }
    ]

    result = _analyze_projects_content(projects)

    assert result == [
        {
            "index": 0,
            "bullet_count": 3,
            "content_length": (
                len("Built a scalable API")
                + len("Improved response time by 40%")
                + len("Handled 10,000 users")
            ),
            "has_metrics": True,
        }
    ]


def test_project_content_without_description():
    projects = [
        {}
    ]

    result = _analyze_projects_content(projects)

    assert result == [
        {
            "index": 0,
            "bullet_count": 0,
            "content_length": 0,
            "has_metrics": False,
        }
    ]


def test_project_content_without_metrics():
    projects = [
        {
            "description": [
                "Built a REST API using FastAPI",
                "Added authentication and authorization",
            ]
        }
    ]

    result = _analyze_projects_content(projects)

    assert result == [
        {
            "index": 0,
            "bullet_count": 2,
            "content_length": (
                len("Built a REST API using FastAPI")
                + len("Added authentication and authorization")
            ),
            "has_metrics": False,
        }
    ]


def test_multiple_project_content():
    projects = [
        {
            "description": [
                "Built a web application",
                "Improved performance by 25%",
            ]
        },
        {
            "description": [
                "Created a REST API",
            ]
        },
    ]

    result = _analyze_projects_content(projects)

    assert result == [
        {
            "index": 0,
            "bullet_count": 2,
            "content_length": (
                len("Built a web application")
                + len("Improved performance by 25%")
            ),
            "has_metrics": True,
        },
        {
            "index": 1,
            "bullet_count": 1,
            "content_length": len("Created a REST API"),
            "has_metrics": False,
        },
    ]


def test_has_metrics_percentage():
    description = [
        "Improved application performance by 30%"
    ]

    assert _has_metrics(description) is True


def test_has_metrics_percent_word():
    description = [
        "Reduced page loading time by 15 percent"
    ]

    assert _has_metrics(description) is True


def test_has_metrics_multiplier():
    description = [
        "Improved throughput by 2x"
    ]

    assert _has_metrics(description) is True


def test_has_metrics_number_with_comma():
    description = [
        "Served more than 10,000 users"
    ]

    assert _has_metrics(description) is True


def test_has_metrics_without_metric():
    description = [
        "Built a scalable web application",
        "Implemented user authentication",
    ]

    assert _has_metrics(description) is False


def test_has_metrics_empty_description():
    assert _has_metrics([]) is False


def test_has_metrics_year_is_not_metric():
    description = [
        "Graduated from NIT Agartala in 2024"
    ]

    assert _has_metrics(description) is False

def test_education_consistency_valid_duration():
    education = [
        {
            "start_year": 2020,
            "end_year": 2024,
        }
    ]

    result = _analyze_education_consistency(education)

    assert result == []

def test_education_consistency_invalid_duration():
    education = [
        {
            "start_year": 2024,
            "end_year": 2020,
        }
    ]

    result = _analyze_education_consistency(education)

    assert result == [
        {
            "section": "education",
            "index": 0,
            "issue": "invalid_duration",
        }
    ]