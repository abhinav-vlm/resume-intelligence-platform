from io import BytesIO
import fitz
import pytest
from fastapi import UploadFile

from src.services.jd_service import process_jd


@pytest.mark.asyncio
async def test_process_jd_text():

    text = "Backend Engineer\nPython\nFastAPI\nSQL"

    result = await process_jd(text)

    assert result["text"] == text

    assert result["jd"] == {
        "role": None,
        "experience": None,    
        "skills":[
        "Python",
        "FastAPI",
        "SQL"],
        "skill_specific_experience": [],
        "skill_requirements": [
            {
                "line": "Backend Engineer",
                "requirement": "unknown",
            },
            {
                "line": "Python",
                "requirement": "unknown",
            },
            {
                "line": "FastAPI",
                "requirement": "unknown",
            },
            {
                "line": "SQL",
                "requirement": "unknown",
            },
        ],
    }


@pytest.mark.asyncio
async def test_process_jd_file():

    doc = fitz.open()

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
            "experience": 3,
        },
        {
            "skill": "AWS",
            "experience": 2,
        },
    ]