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


def patch_pipeline_dependencies(monkeypatch):
    """
    Isolate process_resume() so pipeline behavior can be tested
    without invoking the real parsers/analyzers.
    """

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
        lambda text: None,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_skills",
        lambda text: {
            "known": [],
            "unknown": [],
        },
    )

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

    monkeypatch.setattr(
        resume_service,
        "process_projects",
        lambda text_blocks, links: [],
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_completeness",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_quality",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_formatting",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "process_skill_experience",
        lambda experience, skills: {},
    )


# ============================================================
# PDF input pipeline
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_does_not_process_non_pdf(monkeypatch):
    file = UploadFile(
        filename="resume.txt",
        file=BytesIO(b"fake resume"),
        headers={"content-type": "text/plain"},
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "PDF parser should not be called for non-PDF input"
        )

    monkeypatch.setattr(
        resume_service,
        "extract_text",
        fail_if_called,
    )

    result = await resume_service.process_resume(file)

    assert result == {
        "error": "Only PDF files allowed"
    }


@pytest.mark.asyncio
async def test_process_resume_passes_uploaded_content_to_pdf_pipeline(
    monkeypatch,
):
    uploaded_content = b"realistic fake pdf bytes"

    calls = {}

    def fake_extract_text(content):
        calls["text_content"] = content
        return "Resume text"

    def fake_extract_text_blocks(content):
        calls["block_content"] = content
        return []

    def fake_extract_links(content):
        calls["link_content"] = content
        return []

    monkeypatch.setattr(
        resume_service,
        "extract_text",
        fake_extract_text,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_text_blocks",
        fake_extract_text_blocks,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_links",
        fake_extract_links,
    )

    monkeypatch.setattr(
        resume_service,
        "clean_text",
        lambda text: text,
    )

    monkeypatch.setattr(
        resume_service,
        "detect_sections",
        lambda text: [],
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
        lambda text: None,
    )

    monkeypatch.setattr(
        resume_service,
        "extract_skills",
        lambda text: {
            "known": [],
            "unknown": [],
        },
    )

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

    monkeypatch.setattr(
        resume_service,
        "process_projects",
        lambda text_blocks, links: [],
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_completeness",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_quality",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "analyze_formatting",
        lambda data: {},
    )

    monkeypatch.setattr(
        resume_service,
        "process_skill_experience",
        lambda experience, skills: {},
    )

    file = UploadFile(
        filename="test_resume.pdf",
        file=BytesIO(uploaded_content),
        headers={"content-type": "application/pdf"},
    )

    await resume_service.process_resume(file)

    assert calls["text_content"] == uploaded_content
    assert calls["block_content"] == uploaded_content
    assert calls["link_content"] == uploaded_content


# ============================================================
# Text cleaning → section detection pipeline
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_detects_sections_from_cleaned_text(
    monkeypatch,
):
    raw_text = "  RAW   RESUME   TEXT  "
    cleaned_text = "RAW RESUME TEXT"

    calls = {}

    monkeypatch.setattr(
        resume_service,
        "extract_text",
        lambda content: raw_text,
    )

    def fake_clean_text(text):
        calls["clean_text_input"] = text
        return cleaned_text

    def fake_detect_sections(text):
        calls["detect_sections_input"] = text
        return []

    monkeypatch.setattr(
        resume_service,
        "clean_text",
        fake_clean_text,
    )

    monkeypatch.setattr(
        resume_service,
        "detect_sections",
        fake_detect_sections,
    )

    patch_pipeline_dependencies(monkeypatch)

    await resume_service.process_resume(
        make_pdf_upload()
    )

    assert calls["clean_text_input"] == raw_text
    assert calls["detect_sections_input"] == cleaned_text


# ============================================================
# Upload read behavior
# ============================================================

@pytest.mark.asyncio
async def test_process_resume_reads_uploaded_pdf_content_once(
    monkeypatch,
):
    uploaded_content = b"fake pdf content"

    calls = []

    async def fake_read():
        calls.append(True)
        return uploaded_content

    file = UploadFile(
        filename="test_resume.pdf",
        file=BytesIO(uploaded_content),
        headers={"content-type": "application/pdf"},
    )

    monkeypatch.setattr(
        file,
        "read",
        fake_read,
    )

    patch_pipeline_dependencies(monkeypatch)

    monkeypatch.setattr(
        resume_service,
        "extract_text",
        lambda content: "",
    )

    monkeypatch.setattr(
        resume_service,
        "clean_text",
        lambda text: text,
    )

    monkeypatch.setattr(
        resume_service,
        "detect_sections",
        lambda text: [],
    )

    await resume_service.process_resume(file)

    assert len(calls) == 1
@pytest.mark.asyncio
async def test_process_resume_extracts_linkedin_from_pdf_links(
    monkeypatch,
):
    # Apply the baseline isolation first.
    patch_pipeline_dependencies(monkeypatch)

    # Then override the specific dependency this test cares about.
    monkeypatch.setattr(
        resume_service,
        "extract_text",
        lambda content: "",
    )

    monkeypatch.setattr(
        resume_service,
        "extract_links",
        lambda content: [
            {
                "url": "https://www.linkedin.com/in/test-user",
                "bbox": (),
                "page": 0,
            }
        ],
    )

    monkeypatch.setattr(
        resume_service,
        "extract_text_blocks",
        lambda content: [],
    )

    monkeypatch.setattr(
        resume_service,
        "clean_text",
        lambda text: text,
    )

    monkeypatch.setattr(
        resume_service,
        "detect_sections",
        lambda text: [],
    )

    result = await resume_service.process_resume(
        make_pdf_upload()
    )

    assert result["linkedin"] == (
        "https://www.linkedin.com/in/test-user"
    )