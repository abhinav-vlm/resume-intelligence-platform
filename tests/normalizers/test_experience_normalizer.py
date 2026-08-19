import pytest

from src.normalizers.experience_normalizer import (
    normalize_experience,
    _normalize_duration,
)


def test_normalize_duration_four():
    duration = "January - February, 2024"

    result = _normalize_duration(duration)

    assert result == ("January", "February", 2024, 2024)


def test_normalize_duration_two_month():
    duration = "January 2024"

    result = _normalize_duration(duration)

    assert result == ("January", None, 2024, None)


def test_normalize_duration_two_year():
    duration = "2022 - 2024"

    result = _normalize_duration(duration)

    assert result == (None, None, 2022, 2024)


def test_normalize_duration_one():
    duration = "2024"

    result = _normalize_duration(duration)

    assert result == (None, None, 2024, None)


def test_normalize_experience():
    experience = [
        {
            "company": "Gosotek",
            "duration": "January - February, 2024",
            "role": "Front-End Software Engineering (Remote Intern)",
            "description": [
                "• Utilized Latest technology in Next library"
            ],
        }
    ]

    result = normalize_experience(experience)

    assert result[0] == {
        "company": "Gosotek",
        "start_month": "January",
        "end_month": "February",
        "start_year": 2024,
        "end_year": 2024,
        "position": "Front-End Software Engineering",
        "employment_type": "intern",
        "description": [
            "• Utilized Latest technology in Next library"
        ],
    }
   
   
def test_normalize_experience_without_employment_type():
    experience = [
        {
            "company": "Google",
            "duration": "2024 - 2025",
            "role": "Software Engineer",
            "description": [],
        }
    ]

    result = normalize_experience(experience)

    assert result[0]["position"] == "Software Engineer"
    assert result[0]["employment_type"] is None
   
def test_normalize_experience_without_duration_role():
    experience = [
        {
            "company": "Google",
            "description": [
               "• Utilized Latest technology in Next library"
            ],
        }
    ]

    result = normalize_experience(experience)
    assert result[0]["start_month"] is None
    assert result[0]["end_month"] is None
    assert result[0]["start_year"] is None
    assert result[0]["end_year"] is None
    assert result[0]["company"] == "Google"
    assert result[0]["position"] is None
    assert result[0]["employment_type"] is None


@pytest.mark.parametrize(
    "duration, expected",
    [
        (None, (None, None, None, None)),
        ("", (None, None, None, None)),
        ("   ", (None, None, None, None)),
        ("2024", (None, None, 2024, None)),
        ("2022 - 2024", (None, None, 2022, 2024)),
        ("January 2024", ("January", None, 2024, None)),
        ("January - February, 2024", ("January", "February", 2024, 2024)),
    ],
)
def test_normalize_duration_edge_cases(duration, expected):
    assert _normalize_duration(duration) == expected

@pytest.mark.parametrize(
    "role, expected",
    [
        ("Software Engineer Intern", "intern"),
        ("Software Engineer Internship", "intern"),
        ("Backend Engineer Contract", "contract"),
        ("Backend Engineer Contractual", "contract"),
        ("Frontend Developer Part Time", "part-time"),
        ("Frontend Developer Part-Time", "part-time"),
        ("Software Engineer Full Time", "full-time"),
        ("Software Engineer Full-Time", "full-time"),
        ("Freelance Developer", "freelance"),
        ("Temporary Developer", "temporary"),
        ("Apprentice Developer", "apprentice"),
        ("Graduate Trainee", "trainee"),
        ("Software Engineer", None),
        (None, None),
        ("", None),
        ("   ", None),
    ],
)
def test_normalize_employment_type_variants(role, expected):
    experience = [
        {
            "company": "Test Company",
            "duration": "2024",
            "role": role,
            "description": [],
        }
    ]

    result = normalize_experience(experience)

    assert result[0]["employment_type"] == expected

@pytest.mark.parametrize(
    "role, expected_position",
    [
        (
            "Software Engineer (Remote Intern)",
            "Software Engineer",
        ),
        (
            "Backend Developer - Contract",
            "Backend Developer",
        ),
        (
            "Frontend Developer - Part-Time",
            "Frontend Developer",
        ),
        (
            "Software Engineer",
            "Software Engineer",
        ),
        (
            None,
            None,
        ),
        (
            "",
            None,
        ),
    ],
)
def test_normalize_position_variants(role, expected_position):
    experience = [
        {
            "company": "Test Company",
            "duration": "2024",
            "role": role,
            "description": [],
        }
    ]

    result = normalize_experience(experience)

    assert result[0]["position"] == expected_position

@pytest.mark.parametrize(
    "experience",
    [
        [],
        [
            {
                "company": None,
                "duration": None,
                "role": None,
                "description": [],
            }
        ],
    ],
)
def test_normalize_experience_missing_data(experience):
    result = normalize_experience(experience)

    if not experience:
        assert result == []
        return

    assert result[0]["company"] is None
    assert result[0]["position"] is None
    assert result[0]["employment_type"] is None
    assert result[0]["start_month"] is None
    assert result[0]["end_month"] is None
    assert result[0]["start_year"] is None
    assert result[0]["end_year"] is None

@pytest.mark.parametrize(
    "role, expected_position, expected_employment_type",
    [
        (None, None, None),
        ("", None, None),
        ("   ", None, None),
    ],
)
def test_normalize_empty_role(
    role,
    expected_position,
    expected_employment_type,
):
    experience = [
        {
            "company": "Google",
            "duration": "2024",
            "role": role,
            "description": [],
        }
    ]

    result = normalize_experience(experience)

    assert result[0]["position"] == expected_position
    assert result[0]["employment_type"] == expected_employment_type


def test_normalize_multiple_experience():
    experience = [
        {
            "company": "Google",
            "duration": "2022 - 2024",
            "role": "Software Engineer",
            "description": [],
        },
        {
            "company": "Microsoft",
            "duration": "January - March, 2025",
            "role": "Software Engineer Intern",
            "description": [],
        },
    ]

    result = normalize_experience(experience)

    assert len(result) == 2

    assert result[0]["company"] == "Google"
    assert result[0]["employment_type"] is None

    assert result[1]["company"] == "Microsoft"
    assert result[1]["employment_type"] == "intern"