from src.analyzers.completeness_analyzer import analyze_completeness
import pytest

def test_complete_resume():
    resume = {
        "name": "Abhinav",
        "email": "test@example.com",
        "phone": "+91 1234567890",
        "linkedin": "https://linkedin.com/in/test",
        "education": [{"institution": "NIT"}],
        "experience": [{"company": "Google"}],
        "projects": [{"project": "Resume Parser"}],
        "skills": ["Python"],
    }

    result = analyze_completeness(resume)

    assert all(result["required"].values())
    assert all(result["recommended"].values())

    assert result["missing_required"] == []
    assert result["missing_recommended"] == []

@pytest.mark.parametrize(
"field",
    [
        "name",
        "email",
        "education",
        "projects",
        "skills",
    ],
)
def test_missing_required_field(field):
    resume = {
        "name": "Abhinav",
        "email": "test@example.com",
        "education": [{"institution": "NIT"}],
        "projects": [{"project": "Test"}],
        "skills": ["Python"],
    }

    resume[field] = None

    result = analyze_completeness(resume)

    assert result["required"][field] is False
    assert field in result["missing_required"]

@pytest.mark.parametrize(
    "field",
    [
        "phone",
        "linkedin",
        "experience",
    ],
)
def test_missing_recommended_field(field):
    resume = {
        "name": "Abhinav",
        "email": "test@example.com",
        "education": [{"institution": "NIT"}],
        "projects": [{"project": "Test"}],
        "skills": ["Python"],
        "phone": "+91 1234567890",
        "linkedin": "https://linkedin.com/in/test",
        "experience": [{"company": "Google"}],
    }

    resume[field] = None

    result = analyze_completeness(resume)

    assert result["recommended"][field] is False
    assert field in result["missing_recommended"]

@pytest.mark.parametrize(
    "field",
    [
        "education",
        "projects",
        "skills",
        "experience",
    ],
)
def test_empty_collection_is_missing(field):
    resume = {
        "name": "Abhinav",
        "email": "test@example.com",
        "education": [{"institution": "NIT"}],
        "projects": [{"project": "Test"}],
        "skills": ["Python"],
        "experience": [{"company": "Google"}],
    }

    resume[field] = []

    result = analyze_completeness(resume)

    if field in result["required"]:
       assert result["required"][field] is False
    else:
       assert result["recommended"][field] is False

@pytest.mark.parametrize(
    "field",
    [
        "name",
        "email",
        "phone",
        "linkedin",
    ],
)
def test_empty_scalar_is_missing(field):
    resume = {
        "name": "Abhinav",
        "email": "test@example.com",
        "phone": "+91 1234567890",
        "linkedin": "https://linkedin.com/in/test",
        "education": [{"institution": "NIT"}],
        "projects": [{"project": "Test"}],
        "skills": ["Python"],
        "experience": [{"company": "Google"}],
    }

    resume[field] = ""

    result = analyze_completeness(resume)

    category = "required" if field in result["required"] else "recommended"

    assert result[category][field] is False
