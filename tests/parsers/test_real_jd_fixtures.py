from pathlib import Path
import pytest
from fastapi import UploadFile

from src.parsers.pdf_parser import extract_text
from src.parsers.jd_parser import parse_jd
from src.services.jd_service import process_jd


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


def test_jd_ml_engineer_test_pdf_fixture_exists():
    pdf_path = FIXTURES_DIR / "jd_ml_engineer_test.pdf"
    txt_path = FIXTURES_DIR / "jd_ml_engineer_test.txt"
    assert pdf_path.exists(), "jd_ml_engineer_test.pdf fixture must exist"
    assert txt_path.exists(), "jd_ml_engineer_test.txt fixture must exist"


def test_meta_ml_jd_pdf_fixture_exists():
    assert (FIXTURES_DIR / "Meta_ML_JD.pdf").exists()
    assert (FIXTURES_DIR / "Meta ML JD.pdf").exists()


def test_databricks_se_jd_pdf_fixture_exists():
    assert (FIXTURES_DIR / "Databricks_SE_JD.pdf").exists()
    assert (FIXTURES_DIR / "Databricks SE JD.pdf").exists()


def test_deepmind_research_engineer_jd_pdf_fixture_exists():
    assert (FIXTURES_DIR / "DeepMind_Research_Engineer_JD.pdf").exists()
    assert (FIXTURES_DIR / "DeepMind Research Engineer JD.pdf").exists()


def test_stripe_backend_jd_pdf_fixture_exists():
    assert (FIXTURES_DIR / "Stripe_Backend_JD.pdf").exists()
    assert (FIXTURES_DIR / "Stripe Backend JD.pdf").exists()


def test_extract_skills_jd_ml_engineer_test():
    pdf_path = FIXTURES_DIR / "jd_ml_engineer_test.pdf"
    text = extract_text(pdf_path.read_bytes())
    parsed = parse_jd(text)
    extracted = {s.lower() for s in parsed["skills"]}

    expected = [
        "Python",
        "SQL",
        "FastAPI",
        "Docker",
        "AWS",
        "Kubernetes",
        "PyTorch",
        "MLflow",
        "Scikit-learn",
    ]

    matched = [s for s in expected if s.lower() in extracted]
    rate = len(matched) / len(expected)
    assert rate >= 0.90, f"Extraction rate {rate:.1%} is below 90%"


def test_extract_skills_meta_ml_jd():
    pdf_path = FIXTURES_DIR / "Meta_ML_JD.pdf"
    text = extract_text(pdf_path.read_bytes())
    parsed = parse_jd(text)
    extracted = {s.lower() for s in parsed["skills"]}

    expected = [
        "Python",
        "SQL",
        "Docker",
        "Kubernetes",
        "PyTorch",
        "TensorFlow",
    ]

    matched = [s for s in expected if s.lower() in extracted]
    rate = len(matched) / len(expected)
    assert rate >= 0.90, f"Extraction rate {rate:.1%} is below 90%"


def test_extract_skills_databricks_se_jd():
    pdf_path = FIXTURES_DIR / "Databricks_SE_JD.pdf"
    text = extract_text(pdf_path.read_bytes())
    parsed = parse_jd(text)
    extracted = {s.lower() for s in parsed["skills"]}

    expected = [
        "Python",
        "Java",
        "SQL",
        "Kubernetes",
        "AWS",
        "Docker",
        "Git",
        "Spark",
        "MLflow",
    ]

    matched = [s for s in expected if s.lower() in extracted]
    rate = len(matched) / len(expected)
    assert rate >= 0.90, f"Extraction rate {rate:.1%} is below 90%"


def test_extract_skills_deepmind_research_engineer_jd():
    pdf_path = FIXTURES_DIR / "DeepMind_Research_Engineer_JD.pdf"
    text = extract_text(pdf_path.read_bytes())
    parsed = parse_jd(text)
    extracted = {s.lower() for s in parsed["skills"]}

    expected = [
        "Python",
        "PyTorch",
        "JAX",
        "TensorFlow",
    ]

    matched = [s for s in expected if s.lower() in extracted]
    rate = len(matched) / len(expected)
    assert rate >= 0.90, f"Extraction rate {rate:.1%} is below 90%"


def test_extract_skills_stripe_backend_jd():
    pdf_path = FIXTURES_DIR / "Stripe_Backend_JD.pdf"
    text = extract_text(pdf_path.read_bytes())
    parsed = parse_jd(text)
    extracted = {s.lower() for s in parsed["skills"]}

    expected = [
        "Python",
        "Java",
        "SQL",
        "Docker",
        "Kafka",
        "Scikit-learn",
        "PyTorch",
    ]

    matched = [s for s in expected if s.lower() in extracted]
    rate = len(matched) / len(expected)
    assert rate >= 0.90, f"Extraction rate {rate:.1%} is below 90%"


def test_aggregate_real_jd_fixtures_extraction_rate_exceeds_90_percent():
    cases = [
        (
            "jd_ml_engineer_test.pdf",
            ["Python", "SQL", "FastAPI", "Docker", "AWS", "Kubernetes", "PyTorch", "MLflow", "Scikit-learn"],
        ),
        (
            "Meta_ML_JD.pdf",
            ["Python", "SQL", "Docker", "Kubernetes", "PyTorch", "TensorFlow"],
        ),
        (
            "Databricks_SE_JD.pdf",
            ["Python", "Java", "SQL", "Kubernetes", "AWS", "Docker", "Git", "Spark", "MLflow"],
        ),
        (
            "DeepMind_Research_Engineer_JD.pdf",
            ["Python", "PyTorch", "JAX", "TensorFlow"],
        ),
        (
            "Stripe_Backend_JD.pdf",
            ["Python", "Java", "SQL", "Docker", "Kafka", "Scikit-learn", "PyTorch"],
        ),
    ]

    total_expected = 0
    total_extracted = 0

    for filename, expected in cases:
        pdf_path = FIXTURES_DIR / filename
        text = extract_text(pdf_path.read_bytes())
        parsed = parse_jd(text)
        extracted = {s.lower() for s in parsed["skills"]}

        matched = [s for s in expected if s.lower() in extracted]
        total_expected += len(expected)
        total_extracted += len(matched)

    aggregate_rate = total_extracted / total_expected
    assert aggregate_rate >= 0.90, f"Aggregate extraction rate {aggregate_rate:.1%} is below 90%"


@pytest.mark.asyncio
async def test_process_jd_service_with_real_pdf_fixture():
    fixture_path = FIXTURES_DIR / "jd_ml_engineer_test.pdf"
    file = UploadFile(
        filename=fixture_path.name,
        file=fixture_path.open("rb"),
        headers={"content-type": "application/pdf"},
    )

    result = await process_jd(file)
    assert "jd" in result
    jd = result["jd"]
    assert "skills" in jd
    skills = [s.lower() for s in jd["skills"]]
    assert "python" in skills
    assert "pytorch" in skills
    assert "fastapi" in skills
    assert "docker" in skills
