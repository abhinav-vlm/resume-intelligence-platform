import pytest
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

        "projects": [
            {
                "project": "ML API",
                "metadata": [
                    {
                        "type": "github",
                        "url": "https://github.com/example/ml-api"
                    }
                ],
                "description": [
                    "Built a machine learning API using Python and FastAPI.",
                    "Used SQL for data storage."
                ]
            }
        ],
    }

    jd_data = {
        "role": "ML Engineer",

        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ],

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

    # --------------------------------------------------
    # Skill Match
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Total Experience Match
    # --------------------------------------------------

    assert result["experience_match"]["required"] == 24
    assert result["experience_match"]["candidate"] == 36
    assert result["experience_match"]["difference"] == -12
    assert result["experience_match"]["status"] == "meets"

    # --------------------------------------------------
    # Skill Experience Match
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Role Match
    # --------------------------------------------------

    assert result["role_match"]["candidate_roles"] == [
        "Machine Learning Engineer"
    ]

    assert result["role_match"]["target_role"] == "ML Engineer"

    assert result["role_match"]["canonical_candidate_roles"] == [
        "machine learning engineer"
    ]

    assert result["role_match"]["canonical_target_role"] == (
        "machine learning engineer"
    )

    assert result["role_match"]["status"] == "match"

    # --------------------------------------------------
    # Project Match
    # --------------------------------------------------

    assert result["project_match"][0]["project"] == "ML API"

    assert result["project_match"][0]["metadata"] == [
        {
            "type": "github",
            "url": "https://github.com/example/ml-api"
        }
    ]

    assert result["project_match"][0]["demonstrated"] == [
        "Python",
        "FastAPI",
    ]

    assert result["project_match"][0]["not_demonstrated"] == [
        "Docker",
    ]

    # --------------------------------------------------
    # Scoring (P5D8)
    # --------------------------------------------------
    assert "scoring" in result
    scoring = result["scoring"]
    assert "overall_score" in scoring
    assert scoring["overall_score"] > 0
    assert scoring["verdict"] in ["Strong Match", "Moderate Match", "Underqualified"]
    assert "breakdown" in scoring
    assert "skills" in scoring["breakdown"]
    assert "experience" in scoring["breakdown"]
    assert "role" in scoring["breakdown"]
    assert "projects" in scoring["breakdown"]
    assert "explanation" in scoring


def test_calculate_match_missing_data():
    """
    Ensure calculate_match handles empty/null fields without crashing,
    producing an explicit score and missing-data flags.
    """
    empty_resume = {
        "skills": [],
        "total_experience_months": None,
        "skill_experience": {},
        "experience": [],
        "projects": [],
    }
    empty_jd = {
        "role": None,
        "skills": [],
        "experience_months": None,
        "skill_specific_experience": [],
    }

    result = calculate_match(empty_resume, empty_jd)

    assert result["skill_match"]["matched"] == []
    assert result["experience_match"]["status"] == "unknown"
    assert result["role_match"]["status"] == "unknown"
    assert result["project_match"] == []
    assert "scoring" in result
    assert result["scoring"]["overall_score"] is not None


def test_compose_match_result_preserves_legacy_contract():
    """
    When compose_match_result is called without scoring, it must return
    strictly the 5 original keys, ensuring complete backward compatibility.
    """
    from src.matching.match_result import compose_match_result

    res = compose_match_result(
        skill_match={"matched": ["Python"]},
        experience_match={"status": "meets"},
        skill_experience_match=[],
        role_match={"status": "match"},
        project_match=[]
    )

    assert set(res.keys()) == {
        "skill_match",
        "experience_match",
        "skill_experience_match",
        "role_match",
        "project_match",
    }
    assert "scoring" not in res


@pytest.mark.asyncio
async def test_match_resume_to_jd_integration_full_path():
    """
    Full async service path test: ingest real resume PDF fixture and
    realistic JD text, verifying calculate_match is called and returns
    both all 5 component match results and composite scoring.
    """
    from io import BytesIO
    from fastapi import UploadFile
    from src.services.matching_service import match_resume_to_jd

    with open("tests/fixtures/HARSHIT_WEBDEV.pdf", "rb") as f:
        pdf_bytes = f.read()

    resume_upload = UploadFile(
        filename="HARSHIT_WEBDEV.pdf",
        file=BytesIO(pdf_bytes),
    )

    jd_text = (
        "Frontend Engineer\n"
        "Requirements:\n"
        "• 2+ years of experience in React\n"
        "• JavaScript, HTML, CSS\n"
        "• Python (optional)\n"
    )

    result = await match_resume_to_jd(resume_upload, jd_text)

    # 1. Verify prior 5 response fields exist
    assert "skill_match" in result
    assert "experience_match" in result
    assert "skill_experience_match" in result
    assert "role_match" in result
    assert "project_match" in result

    # 2. Verify scoring field exists with required structure
    assert "scoring" in result
    scoring = result["scoring"]
    assert "overall_score" in scoring
    assert "verdict" in scoring
    assert "breakdown" in scoring
    assert "flags" in scoring
    assert "explanation" in scoring
    assert scoring["overall_score"] >= 0.0
    assert scoring["overall_score"] <= 100.0

def test_calculate_match_matches_identical_unknown_skills():
    resume_data = {
        "skills": [],
        "unknown_skills": ["Workday"],
        "total_experience_months": 36,
        "skill_experience": {},
        "experience": [],
        "projects": [],
    }

    jd_data = {
        "role": "HRIS Analyst",
        "skills": ["Workday"],
        "experience_months": 24,
        "skill_specific_experience": [],
        "skill_requirements": [
            {
                "skill": "Workday",
                "requirement": 'required',
            }
        ],
    }

    result = calculate_match(resume_data, jd_data)

    assert result["skill_match"]["matched"] == ["Workday"]
    assert result["skill_match"]["unmatched"] == []
    assert result["scoring"]["breakdown"]["skills"] == 100.0
    assert "No project evidence provided" in result["scoring"]["flags"]