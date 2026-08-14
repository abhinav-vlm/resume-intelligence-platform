from io import BytesIO
from pathlib import Path
import pytest
from fastapi import UploadFile
from src.normalizers.education_normalizer import normalize_education
from src.normalizers.experience_normalizer import normalize_experience
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
    education = normalize_education(result["education"])[0]

    assert education["institution"] == 'National Institute of Technology, Agartala'
    assert education["degree"] == 'B.Tech'
    assert education["field"] == 'Electronics and Communication Engineering'
    assert education["start_year"] == 2020
    assert education["end_year"] == 2024
    assert education["score"] == 8.3
    assert education["score_type"] == 'CGPA'
    assert result["skills"]

    experience = normalize_experience(result["experience"])[0]
    assert experience["company"] == "Gosotek"
    assert experience["start_month"] == "January"
    assert experience["end_month"] == "February"
    assert experience["start_year"] == 2024
    assert experience["end_year"] == 2024
    assert experience["position"] == "Front-End Software Engineering (Remote Intern)"
    assert experience["description"] == [
        "• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and",
        "• The application named Manhunter Securities was created and improves upto 25 percent effeciency.",
        "• Tools and Technologies used: Javascript, ReactJS, NextJs, CSS"
      ]