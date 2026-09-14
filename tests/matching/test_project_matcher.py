from src.matching.project_matcher import match_project


def test_match_project_demonstrates_jd_skills():

    projects = [
        {
            "project": "ML API",
            "metadata": [],
            "description": [
                "Built a machine learning API using Python and FastAPI.",
                "Used SQL for data storage."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "FastAPI",
        "Docker"
    ]

    result = match_project(projects, jd_skills)

    assert result == [
        {
            "project": "ML API",
            "metadata": [],
            "demonstrated": [
                "Python",
                "FastAPI"
            ],
            "not_demonstrated": [
                "Docker"
            ]
        }
    ]


def test_match_project_multiple_projects():

    projects = [
        {
            "project": "ML API",
            "metadata": [],
            "description": [
                "Built an API using Python and FastAPI."
            ]
        },
        {
            "project": "Frontend App",
            "metadata": [],
            "description": [
                "Built a frontend application using React and JavaScript."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "FastAPI",
        "React",
        "Docker"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["demonstrated"] == [
        "Python",
        "FastAPI"
    ]

    assert result[0]["not_demonstrated"] == [
        "React",
        "Docker"
    ]

    assert result[1]["demonstrated"] == [
        "React"
    ]

    assert result[1]["not_demonstrated"] == [
        "Python",
        "FastAPI",
        "Docker"
    ]


def test_match_project_case_insensitive():

    projects = [
        {
            "project": "ML API",
            "metadata": [],
            "description": [
                "Built the application using PYTHON and FASTAPI."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "FastAPI"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["demonstrated"] == [
        "Python",
        "FastAPI"
    ]

    assert result[0]["not_demonstrated"] == []


def test_match_project_no_matching_skills():

    projects = [
        {
            "project": "Frontend App",
            "metadata": [],
            "description": [
                "Built a frontend application using React and JavaScript."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "FastAPI",
        "Docker"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["demonstrated"] == []

    assert result[0]["not_demonstrated"] == [
        "Python",
        "FastAPI",
        "Docker"
    ]


def test_match_project_empty_projects():

    projects = []

    jd_skills = [
        "Python",
        "FastAPI"
    ]

    result = match_project(projects, jd_skills)

    assert result == []


def test_match_project_empty_jd_skills():

    projects = [
        {
            "project": "ML API",
            "metadata": [],
            "description": [
                "Built an API using Python and FastAPI."
            ]
        }
    ]

    jd_skills = []

    result = match_project(projects, jd_skills)

    assert result == [
        {
            "project": "ML API",
            "metadata": [],
            "demonstrated": [],
            "not_demonstrated": []
        }
    ]


def test_match_project_preserves_metadata():

    projects = [
        {
            "project": "ML API",
            "metadata": [
                {
                    "type": "github",
                    "url": "https://github.com/example/ml-api"
                }
            ],
            "description": [
                "Built an API using Python."
            ]
        }
    ]

    jd_skills = [
        "Python"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["metadata"] == [
        {
            "type": "github",
            "url": "https://github.com/example/ml-api"
        }
    ]


def test_match_project_missing_description():

    projects = [
        {
            "project": "Unknown Project",
            "metadata": []
        }
    ]

    jd_skills = [
        "Python"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["demonstrated"] == []

    assert result[0]["not_demonstrated"] == [
        "Python"
    ]


def test_match_project_does_not_treat_resume_only_skills_as_demonstrated():

    projects = [
        {
            "project": "ML API",
            "metadata": [],
            "description": [
                "Built an API using Python."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "Docker"
    ]

    result = match_project(projects, jd_skills)

    assert "Python" in result[0]["demonstrated"]

    assert "Docker" in result[0]["not_demonstrated"]

    assert "Docker" not in result[0]["demonstrated"]


def test_match_project_skill_can_be_found_across_description_lines():

    projects = [
        {
            "project": "ML Platform",
            "metadata": [],
            "description": [
                "Built a machine learning platform.",
                "Developed backend services.",
                "Used Python extensively.",
                "Created APIs using FastAPI."
            ]
        }
    ]

    jd_skills = [
        "Python",
        "FastAPI"
    ]

    result = match_project(projects, jd_skills)

    assert result[0]["demonstrated"] == [
        "Python",
        "FastAPI"
    ]

    assert result[0]["not_demonstrated"] == []