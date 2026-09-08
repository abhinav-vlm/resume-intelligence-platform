from src.analyzers.skill_experience_analyzer import analyze_skill_experience,_merge_intervals,_calculate_months


def test_explicit_skills_are_extracted_with_experience_evidence():
    experience = [
        {
            "company": "Gosotek",
            "start_month": "January",
            "start_year": 2024,
            "end_month": "February",
            "end_year": 2024,
            "description": [
                "Tools and Technologies used: Javascript, ReactJS, NextJs, CSS"
            ],
        }
    ]

    resume_skills = [
        "JavaScript",
        "React",
        "Next.js",
        "CSS",
    ]

    result = analyze_skill_experience(experience, resume_skills)

    skills = [item["skill"] for item in result]

    assert "JavaScript" in skills
    assert "React" in skills
    assert "Next.js" in skills
    assert "CSS" in skills

    for item in result:
        assert item["evidence"]["company"] == "Gosotek"
        assert item["evidence"]["start_month"] == "January"
        assert item["evidence"]["start_year"] == 2024
        assert item["evidence"]["end_month"] == "February"
        assert item["evidence"]["end_year"] == 2024


def test_embedded_skills_are_detected():
    experience = [
        {
            "company": "ABC",
            "start_month": "March",
            "start_year": 2022,
            "end_month": "December",
            "end_year": 2023,
            "description": [
                "Built REST APIs using FastAPI and Python."
            ],
        }
    ]

    resume_skills = [
        "Python",
        "FastAPI",
        "React",
    ]

    result = analyze_skill_experience(experience, resume_skills)

    skills = [item["skill"] for item in result]

    assert "Python" in skills
    assert "FastAPI" in skills
    assert "React" not in skills


def test_unrelated_resume_skills_are_not_detected():
    experience = [
        {
            "company": "ABC",
            "start_month": "March",
            "start_year": 2022,
            "end_month": "December",
            "end_year": 2023,
            "description": [
                "Built REST APIs using FastAPI."
            ],
        }
    ]

    resume_skills = [
        "Python",
        "FastAPI",
        "React",
    ]

    result = analyze_skill_experience(experience, resume_skills)

    skills = [item["skill"] for item in result]

    assert "FastAPI" in skills
    assert "Python" not in skills
    assert "React" not in skills


def test_missing_dates_are_preserved_as_none():
    experience = [
        {
            "company": "ABC",
            "start_month": None,
            "start_year": None,
            "end_month": None,
            "end_year": None,
            "description": [
                "Built APIs using Python."
            ],
        }
    ]

    resume_skills = ["Python"]

    result = analyze_skill_experience(experience, resume_skills)

    assert len(result) == 1
    assert result[0]["skill"] == "Python"

    evidence = result[0]["evidence"]

    assert evidence["company"] == "ABC"
    assert evidence["start_month"] is None
    assert evidence["start_year"] is None
    assert evidence["end_month"] is None
    assert evidence["end_year"] is None


def test_multiple_experience_entries_preserve_their_own_evidence():
    experience = [
        {
            "company": "Company A",
            "start_month": "January",
            "start_year": 2021,
            "end_month": "December",
            "end_year": 2022,
            "description": [
                "Worked with Python."
            ],
        },
        {
            "company": "Company B",
            "start_month": "January",
            "start_year": 2023,
            "end_month": "June",
            "end_year": 2024,
            "description": [
                "Worked with Python and FastAPI."
            ],
        },
    ]

    resume_skills = [
        "Python",
        "FastAPI",
    ]

    result = analyze_skill_experience(experience, resume_skills)

    python_entries = [
        item for item in result
        if item["skill"] == "Python"
    ]

    assert len(python_entries) == 2

    assert python_entries[0]["evidence"]["company"] == "Company A"
    assert python_entries[0]["evidence"]["start_year"] == 2021
    assert python_entries[0]["evidence"]["end_year"] == 2022

    assert python_entries[1]["evidence"]["company"] == "Company B"
    assert python_entries[1]["evidence"]["start_year"] == 2023
    assert python_entries[1]["evidence"]["end_year"] == 2024


def test_empty_description_returns_no_skill_evidence():
    experience = [
        {
            "company": "ABC",
            "start_month": "January",
            "start_year": 2024,
            "end_month": "February",
            "end_year": 2024,
            "description": [],
        }
    ]

    resume_skills = ["Python", "FastAPI"]

    result = analyze_skill_experience(experience, resume_skills)

    assert result == []


def test_empty_experience_returns_empty_result():
    result = analyze_skill_experience(
        experience=[],
        resume_skills=["Python", "FastAPI"],
    )

    assert result == []



def test_skill_evidence_contains_only_expected_fields():
    experience = [
        {
            "company": "ABC",
            "start_month": "January",
            "start_year": 2024,
            "end_month": "February",
            "end_year": 2024,
            "description": [
                "Built APIs using Python."
            ],
        }
    ]

    result = analyze_skill_experience(
        experience=experience,
        resume_skills=["Python"],
    )

    assert set(result[0]["evidence"].keys()) == {
        "company",
        "start_month",
        "start_year",
        "end_month",
        "end_year",
    }

def test_single_interval():
    intervals = [
        ((2021, 1), (2021, 6))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2021, 6))
    ]

def test_separate_intervals():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 9), (2022, 3))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2021, 6)),
        ((2021, 9), (2022, 3))
    ]

def test_adjacent_intervals():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 7), (2021, 12))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2021, 12))
    ]

def test_partially_overlapping_intervals():
    intervals = [
        ((2021, 1), (2022, 8)),
        ((2022, 1), (2023, 3))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2023, 3))
    ]

def test_interval_inside_previous():
    intervals = [
        ((2021, 1), (2024, 12)),
        ((2022, 1), (2023, 6))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2024, 12))
    ]


def test_interval_inside_previous():
    intervals = [
        ((2021, 1), (2024, 12)),
        ((2022, 1), (2023, 6))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2024, 12))
    ]

def test_december_to_january():
    intervals = [
        ((2021, 12), (2022, 1)),
        ((2022, 2), (2022, 6))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 12), (2022, 6))
    ]

def test_empty_intervals():
    assert _merge_intervals([]) == []

def test_multiple_chained_overlaps():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2021, 5), (2022, 3)),
        ((2022, 2), (2023, 1)),
        ((2023, 1), (2023, 8))
    ]

    assert _merge_intervals(intervals) == [
        ((2021, 1), (2023, 8))
    ]

def test_calculate_months_same_month():
    intervals = [
        ((2024, 1), (2024, 1))
    ]

    assert _calculate_months(intervals) == 1

def test_calculate_months_same_year():
    intervals = [
        ((2024, 1), (2024, 6))
    ]

    assert _calculate_months(intervals) == 6

def test_calculate_months_full_year():
    intervals = [
        ((2024, 1), (2024, 12))
    ]

    assert _calculate_months(intervals) == 12

def test_calculate_months_multiple_years():
    intervals = [
        ((2021, 1), (2023, 3))
    ]

    assert _calculate_months(intervals) == 27

def test_calculate_months_december_to_january():
    intervals = [
        ((2021, 12), (2022, 1))
    ]

    assert _calculate_months(intervals) == 2

def test_calculate_months_multiple_intervals():
    intervals = [
        ((2021, 1), (2021, 6)),
        ((2022, 1), (2022, 3))
    ]

    assert _calculate_months(intervals) == 9

def test_calculate_months_empty():
    assert _calculate_months([]) == 0
