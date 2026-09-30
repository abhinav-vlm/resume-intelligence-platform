from io import BytesIO
import pymupdf
import pytest
from fastapi import UploadFile
from fastapi import HTTPException
from src.services.jd_service import process_jd


@pytest.mark.asyncio
async def test_process_jd_text():

    text = "Backend Engineer\nPython\nFastAPI\nSQL"

    result = await process_jd(text)

    assert result["text"] == text

    jd = result["jd"]
    assert jd["role"] is None
    assert jd["experience_months"] is None
    assert jd["skill_specific_experience"] == []

    assert "Python" in jd["skills"]
    assert "FastAPI" in jd["skills"]
    assert "SQL" in jd["skills"]

    # skill_requirements is list[{skill, requirement}] under current contract
    req_map = {r["skill"]: r["requirement"] for r in jd["skill_requirements"]}
    assert req_map["Python"] == "unknown"
    assert req_map["FastAPI"] == "unknown"
    assert req_map["SQL"] == "unknown"


@pytest.mark.asyncio
async def test_process_jd_file():

    doc = pymupdf.open()

    page = doc.new_page()

    page.insert_text(
        (50, 50),
        "Backend Engineer\nPython\nFastAPI\nSQL"
    )

    pdf_bytes = doc.tobytes()

    doc.close()

    file = UploadFile(
        filename="jd.pdf",
        file=BytesIO(pdf_bytes),
    )

    result = await process_jd(file)

    assert result["text"]
    assert result["jd"]["skills"] == [
        "Python",
        "FastAPI",
        "SQL",
    ]

@pytest.mark.asyncio
async def test_process_jd_skill_specific_experience():

    text = (
        "Backend Engineer\n"
        "3 years of Python experience\n"
        "2+ years of AWS experience"
    )

    result = await process_jd(text)

    assert result["jd"]["skill_specific_experience"] == [
        {
            "skill": "Python",
            "experience_months": 36,
        },
        {
            "skill": "AWS",
            "experience_months": 24,
        },
    ]

@pytest.mark.asyncio
async def test_process_jd_invalid_pdf_returns_400():

    file = UploadFile(
        filename="invalid.pdf",
        file=BytesIO(b"this is not a valid pdf"),
    )

    with pytest.raises(HTTPException) as exc_info:
        await process_jd(file)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid PDF file"

@pytest.mark.asyncio
async def test_process_jd_pdf_and_text_paths_produce_same_jd():

    text = (
        "Backend Engineer\n"
        "Python\n"
        "FastAPI\n"
        "SQL"
    )

    text_result = await process_jd(text)

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)

    pdf_bytes = doc.tobytes()
    doc.close()

    file = UploadFile(
        filename="jd.pdf",
        file=BytesIO(pdf_bytes),
    )

    pdf_result = await process_jd(file)

    assert pdf_result["jd"] == text_result["jd"]