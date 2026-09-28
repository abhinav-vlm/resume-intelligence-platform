from pathlib import Path

import pytest
from fastapi import UploadFile

from src.services.resume_service import process_resume


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "R04_MultiPage_Executive.pdf"
)


def make_upload_file():
    return UploadFile(
        filename=FIXTURE.name,
        file=FIXTURE.open("rb"),
        headers={"content-type": "application/pdf"},
    )


@pytest.mark.asyncio
async def test_r04_multipage_experience_entries_survive():
    file = make_upload_file()

    result = await process_resume(file)

    companies = [
        experience["company"]
        for experience in result["experience"]
    ]

    assert "Stripe" in companies
    assert "Goldman Sachs" in companies
    assert "Bloomberg LP" in companies

@pytest.mark.asyncio
async def test_r04_multipage_stripe_entry_is_preserved():
    file = make_upload_file()

    result = await process_resume(file)

    stripe = next(
        experience
        for experience in result["experience"]
        if experience["company"] == "Stripe"
    )

    assert stripe["position"] == "Director of Engineering"
    assert stripe["start_year"] == 2022


@pytest.mark.asyncio
async def test_r04_multipage_goldman_entry_does_not_absorb_stripe_bullets():
    file = make_upload_file()

    result = await process_resume(file)

    goldman = next(
        experience
        for experience in result["experience"]
        if experience["company"] == "Goldman Sachs"
    )

    description = "\n".join(goldman["description"])

    assert "Led engineering organization of 45 engineers" not in description
    assert "Improved system throughput by 35 percent" not in description

    assert "Directed architecture of high-frequency distributed trading platform" in description
    assert "Managed 30 software engineers" in description

@pytest.mark.asyncio
async def test_r04_multipage_education_entries_survive():
    file = make_upload_file()

    result = await process_resume(file)

    institutions = [
        education["institution"]
        for education in result["education"]
    ]

    assert "Columbia University" in institutions
    assert "Indian Institute of Technology, Delhi" in institutions

