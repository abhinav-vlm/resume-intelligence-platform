from io import BytesIO

import pytest
from fastapi import UploadFile

import src.services.resume_service as resume_service


# ============================================================
# Helpers
# ============================================================

def make_pdf_upload():
    return UploadFile(
        filename="test_resume.pdf",
        file=BytesIO(b"fake pdf content"),
        headers={"content-type": "application/pdf"},
    )


def patch_common_dependencies(monkeypatch, text):
    monkeypatch.setattr(
        resume_service,
        "extract_text",
        lambda content: text,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_text_blocks",
        lambda content: [],
    )

    monkeypatch.setattr(
        resume_service,
        "extract_links",
        lambda content: [],
    )

    monkeypatch.setattr(
        resume_service,
        "extract_email",
        lambda text: None,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_phone",
        lambda text: None,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_name",
        lambda text: "Test User",
    )

    monkeypatch.setattr(
        resume_service,
        "process_projects",
        lambda text_blocks, links: [],
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_completeness",
        lambda resume_data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_quality",
        lambda resume_data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_formatting",
        lambda resume_data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "process_skill_experience",
        lambda experience, skills: {},
    )


# ============================================================
# File validation
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_rejects_non_pdf():
    file = UploadFile(
        filename="resume.txt",
        file=BytesIO(b"fake resume"),
        headers={"content-type": "text/plain"},
    )

    result = await resume_service.process_resume(file)

    assert result == {
        "error": "Only PDF files allowed"
    }


@pytest.mark.asyncio
async def test_process_resume_does_not_process_non_pdf(monkeypatch):
    file = UploadFile(
        filename="resume.txt",
        file=BytesIO(b"fake resume"),
        headers={"content-type": "text/plain"},
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("PDF parser should not be called")

    monkeypatch.setattr(
        resume_service,
        "extract_text",
        fail_if_called,
    )

    result = await resume_service.process_resume(file)

    assert result == {
        "error": "Only PDF files allowed"
    }


# ============================================================
# Section-aware experience integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_routes_experience_section_to_parser(
    monkeypatch,
):
    text = """WORK EXPERIENCE
Company A
Software Engineer
2022 - 2024
Built ML systems.

EDUCATION
University A
B.Tech
2020 - 2024
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_experience(experience_text):
        captured["text"] = experience_text

        return [
            {
                "company": "Company A",
                "position": "Software Engineer",
            }
        ]

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        fake_process_experience,
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_experience",
        lambda experience: experience,
    )

    monkeypatch.setattr(
        resume_service,
        "calculate_total_experience",
        lambda experience: 0,
    )

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"].strip() == (
        "Company A\n"
        "Software Engineer\n"
        "2022 - 2024\n"
        "Built ML systems."
    )

    assert result["experience"] == [
        {
            "company": "Company A",
            "position": "Software Engineer",
        }
    ]


@pytest.mark.asyncio
async def test_process_resume_aggregates_multiple_experience_sections(
    monkeypatch,
):
    text = """EXPERIENCE
Company A
Software Engineer
2022 - 2024

SUMMARY
Experienced ML engineer.

WORK HISTORY
Company B
Senior Software Engineer
2019 - 2022
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_experience(experience_text):
        captured["text"] = experience_text

        return [
            {"company": "Company A"},
            {"company": "Company B"},
        ]

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        fake_process_experience,
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_experience",
        lambda experience: experience,
    )

    monkeypatch.setattr(
        resume_service,
        "calculate_total_experience",
        lambda experience: 0,
    )

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"].strip() == (
        "Company A\n"
        "Software Engineer\n"
        "2022 - 2024\n"
        "\n"
        "Company B\n"
        "Senior Software Engineer\n"
        "2019 - 2022"
    )

    assert result["experience"] == [
        {"company": "Company A"},
        {"company": "Company B"},
    ]


@pytest.mark.asyncio
async def test_process_resume_returns_empty_experience_when_no_experience_section(
    monkeypatch,
):
    text = """EDUCATION
University A
B.Tech
2020 - 2024

SKILLS
Python
SQL
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_experience(experience_text):
        captured["text"] = experience_text
        return None

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        fake_process_experience,
    )

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"] == ""
    assert result["experience"] == []
    assert result["total_experience_months"] == 0


# ============================================================
# Section-aware education integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_routes_education_section_to_parser(
    monkeypatch,
):
    text = """EDUCATION
University A
B.Tech Computer Science
2020 - 2024

EXPERIENCE
Company A
Software Engineer
2024 - PRESENT
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_education(education_text):
        captured["text"] = education_text

        return [
            {
                "institution": "University A",
                "degree": "B.Tech Computer Science",
            }
        ]

    monkeypatch.setattr(
        resume_service,
        "process_education",
        fake_process_education,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_education",
        lambda education: education,
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"].strip() == (
        "University A\n"
        "B.Tech Computer Science\n"
        "2020 - 2024"
    )

    assert result["education"] == [
        {
            "institution": "University A",
            "degree": "B.Tech Computer Science",
        }
    ]


@pytest.mark.asyncio
async def test_process_resume_aggregates_multiple_education_sections(
    monkeypatch,
):
    text = """EDUCATION
University A
B.Tech
2018 - 2022

ACADEMIC QUALIFICATIONS
University B
M.Tech
2022 - 2024
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_education(education_text):
        captured["text"] = education_text

        return [
            {"institution": "University A"},
            {"institution": "University B"},
        ]

    monkeypatch.setattr(
        resume_service,
        "process_education",
        fake_process_education,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_education",
        lambda education: education,
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"].strip() == (
        "University A\n"
        "B.Tech\n"
        "2018 - 2022\n"
        "\n"
        "University B\n"
        "M.Tech\n"
        "2022 - 2024"
    )

    assert result["education"] == [
        {"institution": "University A"},
        {"institution": "University B"},
    ]


@pytest.mark.asyncio
async def test_process_resume_returns_no_education_when_section_is_absent(
    monkeypatch,
):
    text = """EXPERIENCE
Company A
Software Engineer
2022 - PRESENT

SKILLS
Python
"""

    patch_common_dependencies(monkeypatch, text)

    captured = {}

    def fake_process_education(education_text):
        captured["text"] = education_text
        return None

    monkeypatch.setattr(
        resume_service,
        "process_education",
        fake_process_education,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert captured["text"] == ""
    assert result["education"] is None


# ============================================================
# Skills integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_aggregates_multiple_skill_sections(
    monkeypatch,
):
    text = """TECHNICAL SKILLS
Python
SQL

NON TECHNICAL SKILLS
Communication
Leadership
"""

    patch_common_dependencies(monkeypatch, text)

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["sections"][0]["name"] == "skills"
    assert result["sections"][1]["name"] == "skills"

    assert "Python" in result["skills"]
    assert "SQL" in result["skills"]


# ============================================================
# Service response contract
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_response_contains_expected_contract(
    monkeypatch,
):
    text = """EDUCATION
University A
B.Tech
2020 - 2024

EXPERIENCE
Company A
Software Engineer
2022 - PRESENT

SKILLS
Python
"""

    patch_common_dependencies(monkeypatch, text)

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: None,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    expected_keys = {
        "filename",
        "text",
        "email",
        "phone",
        "name",
        "sections",
        "education",
        "experience",
        "projects",
        "skills",
        "unknown_skills",
        "total_experience_months",
        "completeness",
        "quality_check",
        "formatting_check",
        "skill_experience",
        "content_type",
        "message",
    }

    assert expected_keys.issubset(result.keys())

    assert result["filename"] == "test_resume.pdf"
    assert result["content_type"] == "application/pdf"
    assert result["message"] == "Resume received successfully"


# ============================================================
# Resume metadata extraction
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_extracts_metadata_from_cleaned_text(
    monkeypatch,
):
    text = """John Doe
john@example.com
+91-9876543210

SKILLS
Python
"""

    patch_common_dependencies(monkeypatch, text)

    monkeypatch.setattr(
        resume_service,
        "extract_email",
        lambda text: "john@example.com",
    )

    monkeypatch.setattr(
        resume_service,
        "extract_phone",
        lambda text: "+91-9876543210",
    )

    monkeypatch.setattr(
        resume_service,
        "extract_name",
        lambda text: "John Doe",
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    assert result["phone"] == "+91-9876543210"


# ============================================================
# Projects integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_processes_projects(
    monkeypatch,
):
    text = """PROJECTS
Resume Intelligence Platform
Built a production-grade resume parser.

SKILLS
Python
"""

    patch_common_dependencies(monkeypatch, text)

    monkeypatch.setattr(
        resume_service,
        "process_projects",
        lambda text_blocks, links: [
            {
                "name": "Resume Intelligence Platform",
            }
        ],
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_projects",
        lambda projects: projects,
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["projects"] == [
        {
            "name": "Resume Intelligence Platform",
        }
    ]


# ============================================================
# Normalization integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_normalizes_experience(
    monkeypatch,
):
    text = """EXPERIENCE
Company A
Software Engineer
2022 - 2024
"""

    patch_common_dependencies(monkeypatch, text)

    raw_experience = [
        {
            "company": "Company A",
            "position": "Software Engineer",
        }
    ]

    normalized_experience = [
        {
            "company": "Company A",
            "position": "Software Engineer",
            "duration_months": 24,
        }
    ]

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: raw_experience,
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_experience",
        lambda experience: normalized_experience,
    )

    monkeypatch.setattr(
        resume_service,
        "calculate_total_experience",
        lambda experience: 24,
    )

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["experience"] == normalized_experience
    assert result["total_experience_months"] == 24


@pytest.mark.asyncio
async def test_process_resume_normalizes_education(
    monkeypatch,
):
    text = """EDUCATION
University A
B.Tech
2020 - 2024
"""

    patch_common_dependencies(monkeypatch, text)

    raw_education = [
        {
            "institution": "University A",
            "degree": "B.Tech",
        }
    ]

    normalized_education = [
        {
            "institution": "University A",
            "degree": "B.Tech",
            "start_year": 2020,
            "end_year": 2024,
        }
    ]

    monkeypatch.setattr(
        resume_service,
        "process_education",
        lambda text: raw_education,
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_education",
        lambda education: normalized_education,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["education"] == normalized_education


# ============================================================
# Analyzer integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_runs_resume_analyzers(
    monkeypatch,
):
    text = """EXPERIENCE
Company A
Software Engineer

SKILLS
Python
"""

    patch_common_dependencies(monkeypatch, text)

    calls = {}

    def fake_completeness(data):
        calls["completeness"] = data
        return {"score": 80}

    def fake_quality(data):
        calls["quality"] = data
        return {"score": 75}

    def fake_formatting(data):
        calls["formatting"] = data
        return {"score": 90}

    monkeypatch.setattr(
        resume_service,
        "analyze_completeness",
        fake_completeness,
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_quality",
        fake_quality,
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_formatting",
        fake_formatting,
    )

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["completeness"] == {"score": 80}
    assert result["quality_check"] == {"score": 75}
    assert result["formatting_check"] == {"score": 90}

    assert "completeness" in calls
    assert "quality" in calls
    assert "formatting" in calls


# ============================================================
# Skill-experience integration
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_builds_skill_experience_mapping(
    monkeypatch,
):
    text = """EXPERIENCE
Company A
Python Developer

SKILLS
Python
SQL
"""

    patch_common_dependencies(monkeypatch, text)

    expected_mapping = {
        "Python": {
            "years": 2,
        }
    }

    monkeypatch.setattr(
        resume_service,
        "process_experience",
        lambda text: [
            {
                "company": "Company A",
                "position": "Python Developer",
            }
        ],
    )

    monkeypatch.setattr(
        resume_service,
        "normalize_experience",
        lambda experience: experience,
    )

    monkeypatch.setattr(
        resume_service,
        "calculate_total_experience",
        lambda experience: 24,
    )

    monkeypatch.setattr(
        resume_service,
        "process_skill_experience",
        lambda experience, skills: expected_mapping,
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["skill_experience"] == expected_mapping