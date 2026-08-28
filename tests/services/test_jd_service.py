from io import BytesIO

import pytest
from fastapi import UploadFile

from src.services.jd_service import process_jd


@pytest.mark.asyncio
async def test_process_jd_text():

    text = "Backend Engineer\nPython\nFastAPI"

    result = await process_jd(text)

    assert result["content"] == text

    assert result["jd"] == {
        "role": None,
        "experience": None,
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
        ],
    }


@pytest.mark.asyncio
async def test_process_jd_file():

    content = b"Backend Engineer\nPython\nFastAPI"

    file = UploadFile(
        filename="jd.txt",
        file=BytesIO(content),
    )

    result = await process_jd(file)

    # This test is only valid if the service currently
    # supports decoding the uploaded bytes.
    assert result["content"] == "Backend Engineer\nPython\nFastAPI"

    assert result["jd"] == {
    "role": None,
    "experience": None,
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
    ],
}