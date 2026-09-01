from io import BytesIO

import pytest
from fastapi import UploadFile

from src.services.jd_service import process_jd


@pytest.mark.asyncio
async def test_process_jd_text():

    text = "Backend Engineer\nPython\nFastAPI\nSQL"

    result = await process_jd(text)

    assert result["content"] == text

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

    content = b"Backend Engineer\nPython\nFastAPI\nSQL"

    file = UploadFile(
        filename="jd.txt",
        file=BytesIO(content),
    )

    result = await process_jd(file)

    # This test is only valid if the service currently
    # supports decoding the uploaded bytes.
    assert result["content"] == "Backend Engineer\nPython\nFastAPI\nSQL"

    assert result["jd"] == {
    "role": None,
    "experience": None,
    "skills":[
        "Python",
        "FastAPI",
        "SQL",
    ],
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