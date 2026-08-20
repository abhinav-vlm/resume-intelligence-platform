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
    education = result["education"][0]

    assert education["institution"] == 'National Institute of Technology, Agartala'
    assert education["degree"] == 'B.Tech'
    assert education["field"] == 'Electronics and Communication Engineering'
    assert education["start_year"] == 2020
    assert education["end_year"] == 2024
    assert education["score"] == 8.3
    assert education["score_type"] == 'CGPA'
    assert result["skills"]

    assert "Python" in result["skills"]
    assert "C++" in result["skills"]
    assert "SQL" in result["skills"]
    assert "React" in result["skills"]
    assert "Express.js" in result["skills"]
    assert "Next.js" in result["skills"]
    assert "GitHub" in result["skills"]
    assert "ReactJS" not in result["skills"]
    assert "Express.JS" not in result["skills"]
    assert "Next.JS" not in result["skills"]

    experience = result["experience"][0]
    assert experience["company"] == "Gosotek"
    assert experience["start_month"] == "January"
    assert experience["end_month"] == "February"
    assert experience["start_year"] == 2024
    assert experience["end_year"] == 2024
    assert result["experience"][0]["position"] == "Front-End Software Engineering"
    assert result["experience"][0]["employment_type"] == "intern"
    assert experience["description"] == [
        "• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and",
        "• The application named Manhunter Securities was created and improves upto 25 percent effeciency.",
        "• Tools and Technologies used: Javascript, ReactJS, NextJs, CSS"
      ]
    assert result["projects"][0]["project"] == "Bloger - A Full Stack Blog App | GitHub"

    assert result["projects"][0]["metadata"] == [
       {
        "type": "github",
        "url": "https://github.com/Blockmecoder/Bloger"
      }
      ]

    assert result["projects"][0]["description"] == [
       "• Developed a scalable and efficient full-stack blog application enabling users to create and explore blogs with 15 percent more efficiency.",
       "• Features user authentication, blog posting, editing, and user profile updates.",
       "• Tools and Technologies used : ReactJS, Node.js, Express.js, MongoDB, JavaScript, HTML, CSS"
     ]

    assert result["projects"][1]["metadata"] == [
      {
        "type": "github",
        "url": "https://github.com/Blockmecoder/CITY_APP"
      }
      ]

    assert result["projects"][2]["metadata"] == [
      {
        "type": "github",
        "url": "https://github.com/Blockmecoder/PrompTopic"
      }
      ]

    assert "_bbox" not in result["projects"][0]
    assert "_page" not in result["projects"][0]

    completeness = result["completeness"]

    assert completeness["required"] == {
        "name": True,
        "email": True,
        "education": True,
        "projects": True,
        "skills": True,
    }

    assert completeness["recommended"] == {
        "phone": True,
        "linkedin": False,
        "experience": True,
    }

    assert completeness["missing_required"] == []
    assert completeness["missing_recommended"] == ["linkedin"]