from io import BytesIO
from pathlib import Path
import pytest
from fastapi import UploadFile

from src.services.resume_service import process_resume


async def create_upload_file():
    pdf_path = Path("tests/fixtures/HARSHIT_WEBDEV.pdf")

    content = pdf_path.read_bytes()

    return UploadFile(
        filename=pdf_path.name,
        file=BytesIO(content),
        headers={
            "content-type": "application/pdf"
        }
    )

@pytest.mark.asyncio
async def test_process_resume():
    file = await create_upload_file()

    result = await process_resume(file)

    assert result is not None

    assert result["filename"] == "HARSHIT_WEBDEV.pdf"
    assert result["content_type"] == "application/pdf"
    assert result["message"] == "Resume received successfully"

    assert result["name"] == "Abhinav Pratap Singh"
    assert result["email"] == "apsbqt@gmail.com"
    assert result["phone"] == "+91 9774913812"

    assert len(result["education"]) == 3
    assert len(result["experience"]) == 1
    assert len(result["projects"]) == 3

    assert result["skills"]