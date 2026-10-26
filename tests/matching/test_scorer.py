import pytest
from src.matching.scorer import (
    score_skills,
    score_experience,
    score_role,
    score_projects,
    calculate_composite_score,
    DEFAULT_WEIGHTS,
)


# ==============================================================================
# Skill Scoring Tests
# ==============================================================================

def test_score_skills_all_required_matched():
    skill_match = {
        "matched": ["Python", "FastAPI"],
        "unmatched": [],
        "extra": ["Docker"],
    }
    skill_requirements = [
        {"skill": "Python", "requirement": "required"},
        {"skill": "FastAPI", "requirement": "required"},
    ]
    result = score_skills(skill_match, skill_requirements)

    assert result["score"] == 100.0
    assert result["missing_required"] == []
    assert result["missing_optional"] == []
    assert result["matched_required"] == ["Python", "FastAPI"]
    assert result["flags"]["candidate_skills_missing"] is False
    assert result["flags"]["jd_skills_missing"] is False


def test_score_skills_differentiates_required_and_optional():
    # JD has Python (required) and Docker (optional)
    # Candidate A matches Python (required), misses Docker (optional)
    # Candidate B matches Docker (optional), misses Python (required)
    requirements = [
        {"skill": "Python", "requirement": "required"},
        {"skill": "Docker", "requirement": "optional"},
    ]

    match_a = {"matched": ["Python"], "unmatched": ["Docker"], "extra": []}
    match_b = {"matched": ["Docker"], "unmatched": ["Python"], "extra": []}

    res_a = score_skills(match_a, requirements)
    res_b = score_skills(match_b, requirements)

    # Candidate A who has the required skill must score significantly higher than Candidate B
    assert res_a["score"] > res_b["score"]
    assert "Python" in res_b["missing_required"]
    assert "Docker" in res_a["missing_optional"]


def test_score_skills_without_requirements_treats_all_equal():
    skill_match = {
        "matched": ["Python"],
        "unmatched": ["Docker"],
        "extra": [],
    }
    result = score_skills(skill_match, skill_requirements=None)

    # 1 out of 2 matched -> 50.0
    assert result["score"] == 50.0
    assert result["matched_count"] == 1
    assert result["total_jd_skills"] == 2


def test_score_skills_empty_candidate_skills():
    skill_match = {
        "matched": [],
        "unmatched": ["Python", "Docker"],
        "extra": [],
    }
    result = score_skills(skill_match)

    assert result["score"] == 0.0
    assert result["flags"]["candidate_skills_missing"] is True


def test_score_skills_empty_jd_skills():
    skill_match = {
        "matched": [],
        "unmatched": [],
        "extra": ["Python"],
    }
    result = score_skills(skill_match)

    assert result["score"] == 100.0
    assert result["flags"]["jd_skills_missing"] is True


# ==============================================================================
# Experience Scoring Tests
# ==============================================================================

def test_score_experience_meets_tenure():
    exp_match = {
        "required": 24,
        "candidate": 36,
        "difference": -12,
        "status": "meets",
    }
    result = score_experience(exp_match)

    assert result["score"] == 100.0
    assert result["status"] == "meets"
    assert result["flags"]["candidate_experience_missing"] is False


def test_score_experience_underqualified_proportional():
    exp_match = {
        "required": 24,
        "candidate": 12,
        "difference": 12,
        "status": "underqualified",
    }
    result = score_experience(exp_match)

    # 12 / 24 months = 50.0%
    assert result["score"] == 50.0
    assert result["status"] == "underqualified"
    assert result["gap_months"] == 12


def test_score_experience_candidate_missing():
    exp_match = {
        "required": 24,
        "candidate": None,
        "difference": None,
        "status": "unknown",
    }
    result = score_experience(exp_match)

    assert result["score"] == 0.0
    assert result["flags"]["candidate_experience_missing"] is True


def test_score_experience_jd_unspecified():
    exp_match = {
        "required": None,
        "candidate": 36,
        "difference": None,
        "status": "unknown",
    }
    result = score_experience(exp_match)

    assert result["score"] == 100.0
    assert result["flags"]["jd_experience_unspecified"] is True


def test_score_experience_with_skill_specific_penalty():
    exp_match = {
        "required": 24,
        "candidate": 36,
        "difference": -12,
        "status": "meets",
    }
    skill_exp_match = [
        {
            "skill": "Python",
            "required_experience_months": 24,
            "candidate_experience_months": 12,
            "difference_months": 12,
            "status": "underqualified",
        }
    ]
    result = score_experience(exp_match, skill_exp_match)

    # Base is 100.0, but underqualified in skill-specific tenure applies a penalty
    assert result["score"] < 100.0
    assert "Python" in result["underqualified_skills"]


# ==============================================================================
# Role Scoring Tests
# ==============================================================================

def test_score_role_match():
    role_match = {
        "candidate_roles": ["ML Engineer"],
        "target_role": "ML Engineer",
        "canonical_candidate_roles": ["machine learning engineer"],
        "canonical_target_role": "machine learning engineer",
        "status": "match",
    }
    result = score_role(role_match)

    assert result["score"] == 100.0
    assert result["status"] == "match"
    assert result["flags"]["role_mismatch"] is False


def test_score_role_mismatch():
    role_match = {
        "candidate_roles": ["Frontend Developer"],
        "target_role": "Data Scientist",
        "canonical_candidate_roles": ["frontend developer"],
        "canonical_target_role": "data scientist",
        "status": "mismatch",
    }
    result = score_role(role_match)

    assert result["score"] == 0.0
    assert result["status"] == "mismatch"
    assert result["flags"]["role_mismatch"] is True


def test_score_role_unknown():
    role_match = {
        "candidate_roles": ["Custom Title"],
        "target_role": "Specialist",
        "canonical_candidate_roles": [None],
        "canonical_target_role": None,
        "status": "unknown",
    }
    result = score_role(role_match)

    # Unknown role alignment yields neutral 50.0 score with flag
    assert result["score"] == 50.0
    assert result["status"] == "unknown"
    assert result["flags"]["role_unknown"] is True


# ==============================================================================
# Project Scoring Tests
# ==============================================================================

def test_score_projects_all_skills_demonstrated():
    project_match = [
        {
            "project": "P1",
            "demonstrated": ["Python", "FastAPI"],
            "not_demonstrated": [],
        }
    ]
    result = score_projects(project_match, jd_skills=["Python", "FastAPI"])

    assert result["score"] == 100.0
    assert result["demonstrated_skills"] == ["FastAPI", "Python"]
    assert result["flags"]["no_project_evidence"] is False


def test_score_projects_partial_demonstration():
    project_match = [
        {
            "project": "P1",
            "demonstrated": ["Python"],
            "not_demonstrated": ["Docker"],
        }
    ]
    result = score_projects(project_match, jd_skills=["Python", "Docker"])

    assert result["score"] == 50.0
    assert result["demonstrated_skills"] == ["Python"]


def test_score_projects_empty():
    result = score_projects([], jd_skills=["Python", "Docker"])

    assert result["score"] == 0.0
    assert result["flags"]["no_project_evidence"] is True


# ==============================================================================
# Composite Scoring & Verdict Tests
# ==============================================================================

def test_calculate_composite_score_reproducibility():
    skill_res = {"score": 90.0, "missing_required": [], "flags": {}}
    exp_res = {"score": 100.0, "status": "meets", "gap_months": 0, "flags": {}}
    role_res = {"score": 100.0, "status": "match", "flags": {}}
    proj_res = {"score": 80.0, "flags": {}}

    res1 = calculate_composite_score(skill_res, exp_res, role_res, proj_res)
    res2 = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    assert res1["overall_score"] == res2["overall_score"]
    assert res1["verdict"] == res2["verdict"]
    assert res1["breakdown"] == res2["breakdown"]


def test_calculate_composite_score_strong_match():
    skill_res = {"score": 100.0, "missing_required": [], "flags": {}}
    exp_res = {"score": 100.0, "status": "meets", "gap_months": 0, "flags": {}}
    role_res = {"score": 100.0, "status": "match", "flags": {}}
    proj_res = {"score": 100.0, "flags": {}}

    res = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    assert res["overall_score"] == 100.0
    assert res["verdict"] == "Strong Match"


def test_calculate_composite_score_underqualified_verdict():
    skill_res = {"score": 20.0, "missing_required": ["Python", "SQL"], "flags": {}}
    exp_res = {"score": 25.0, "status": "underqualified", "gap_months": 18, "flags": {}}
    role_res = {"score": 0.0, "status": "mismatch", "flags": {"role_mismatch": True}}
    proj_res = {"score": 0.0, "flags": {"no_project_evidence": True}}

    res = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    assert res["overall_score"] < 50.0
    assert res["verdict"] == "Underqualified"
    assert len(res["flags"]) > 0
    assert "Underqualified" in res["explanation"]


# ==============================================================================
# Phase 5 Verification Gate: Exhaustive Contract & Edge Case Tests
# ==============================================================================

def test_weights_total_100_percent_and_apply_to_intended_dimensions():
    """Verify DEFAULT_WEIGHTS sum to exactly 1.0 (100%) and apply to intended dimensions."""
    assert sum(DEFAULT_WEIGHTS.values()) == pytest.approx(1.0)
    assert DEFAULT_WEIGHTS["skills"] == 0.40
    assert DEFAULT_WEIGHTS["experience"] == 0.25
    assert DEFAULT_WEIGHTS["role"] == 0.20
    assert DEFAULT_WEIGHTS["projects"] == 0.15

    # Each dimension isolated to 100% must yield exactly its designated weight
    skill_only = calculate_composite_score(
        {"score": 100.0, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 0.0},
    )
    assert skill_only["overall_score"] == 40.0

    exp_only = calculate_composite_score(
        {"score": 0.0, "missing_required": []},
        {"score": 100.0},
        {"score": 0.0},
        {"score": 0.0},
    )
    assert exp_only["overall_score"] == 25.0

    role_only = calculate_composite_score(
        {"score": 0.0, "missing_required": []},
        {"score": 0.0},
        {"score": 100.0},
        {"score": 0.0},
    )
    assert role_only["overall_score"] == 20.0

    proj_only = calculate_composite_score(
        {"score": 0.0, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 100.0},
    )
    assert proj_only["overall_score"] == 15.0


def test_relative_weights_required_vs_optional_ratio():
    """Verify required skill carries 2x the weight of an optional skill (2.0 vs 1.0)."""
    requirements = [
        {"skill": "Python", "requirement": "required"},   # weight 2.0
        {"skill": "Docker", "requirement": "optional"},   # weight 1.0
    ]
    # Total weight = 3.0
    match_required = {"matched": ["Python"], "unmatched": ["Docker"], "extra": []}
    match_optional = {"matched": ["Docker"], "unmatched": ["Python"], "extra": []}

    res_req = score_skills(match_required, requirements)
    res_opt = score_skills(match_optional, requirements)

    # 2.0 / 3.0 = 66.7% vs 1.0 / 3.0 = 33.3%
    assert res_req["score"] == 66.7
    assert res_opt["score"] == 33.3
    assert res_req["score"] == pytest.approx(res_opt["score"] * 2.0, abs=0.2)


def test_missing_required_skills_reported_and_penalize():
    """Verify missing required skills are surfaced in output and flags."""
    requirements = [
        {"skill": "Python", "requirement": "required"},
        {"skill": "SQL", "requirement": "required"},
    ]
    match = {"matched": ["Python"], "unmatched": ["SQL"], "extra": []}
    result = score_skills(match, requirements)

    assert result["missing_required"] == ["SQL"]
    assert result["score"] == 50.0

    composite = calculate_composite_score(
        result,
        {"score": 100.0},
        {"score": 100.0},
        {"score": 100.0},
    )
    assert any("SQL" in f for f in composite["flags"])


def test_missing_candidate_skills_or_experience_earn_zero_points():
    """Missing candidate skills or experience must score 0.0, not award points."""
    # Candidate has no skills, JD has skills
    skill_res = score_skills({"matched": [], "unmatched": ["Python", "Go"], "extra": []})
    assert skill_res["score"] == 0.0
    assert skill_res["flags"]["candidate_skills_missing"] is True

    # Candidate experience is None, JD requires 24 months
    exp_res = score_experience({"required": 24, "candidate": None, "difference": None, "status": "unknown"})
    assert exp_res["score"] == 0.0
    assert exp_res["flags"]["candidate_experience_missing"] is True


def test_unspecified_jd_experience_handled_and_flagged():
    """When JD specifies no tenure, candidate receives full experience score with explicit flag."""
    exp_res = score_experience({"required": None, "candidate": 12, "difference": None, "status": "unknown"})
    assert exp_res["score"] == 100.0
    assert exp_res["flags"]["jd_experience_unspecified"] is True


def test_zero_required_experience_no_division_error():
    """Zero required experience (fresher / entry-level) must not cause ZeroDivisionError."""
    # 0 required, 0 candidate
    res1 = score_experience({"required": 0, "candidate": 0, "difference": 0, "status": "meets"})
    assert res1["score"] == 100.0

    # 0 required, 12 candidate
    res2 = score_experience({"required": 0, "candidate": 12, "difference": -12, "status": "meets"})
    assert res2["score"] == 100.0


def test_empty_dictionaries_and_null_values_safe():
    """Verify all scoring functions handle empty dictionaries and None gracefully."""
    # Empty skill match
    s = score_skills({}, None)
    assert s["score"] == 100.0
    assert s["flags"]["jd_skills_missing"] is True

    # Empty experience match
    e = score_experience({}, None)
    assert e["score"] == 100.0
    assert e["flags"]["jd_experience_unspecified"] is True

    # Empty role match
    r = score_role({})
    assert r["score"] == 50.0
    assert r["flags"]["role_unknown"] is True

    # Empty project match
    p = score_projects([], None)
    assert p["score"] == 0.0
    assert p["flags"]["no_project_evidence"] is True

    # Empty composite
    comp = calculate_composite_score({}, {}, {}, {})
    assert comp["overall_score"] == 0.0
    assert comp["verdict"] == "Underqualified"


def test_role_mismatch_cannot_receive_strong_match_even_with_high_score():
    """A candidate with role mismatch must NEVER receive Strong Match, even with >= 80 score."""
    # Skills = 100, Exp = 100, Projects = 100, Role = 0 (mismatch)
    # 0.40*100 + 0.25*100 + 0.20*0 + 0.15*100 = 40 + 25 + 0 + 15 = 80.0!
    skill_res = {"score": 100.0, "missing_required": []}
    exp_res = {"score": 100.0, "gap_months": 0}
    role_res = {"score": 0.0, "flags": {"role_mismatch": True}}
    proj_res = {"score": 100.0, "flags": {}}

    res = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    assert res["overall_score"] == 80.0
    # Must NOT be Strong Match due to role mismatch veto
    assert res["verdict"] == "Moderate Match"
    assert "Role alignment mismatch" in res["flags"]


def test_missing_required_skill_cannot_receive_strong_match_even_at_80():
    """A candidate missing a required skill cannot receive Strong Match at score >= 80."""
    skill_res = {"score": 80.0, "missing_required": ["Python"]}
    exp_res = {"score": 100.0, "gap_months": 0}
    role_res = {"score": 100.0, "flags": {"role_mismatch": False}}
    proj_res = {"score": 80.0, "flags": {}}

    res = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    assert res["overall_score"] >= 80.0
    assert res["verdict"] == "Moderate Match"


def test_threshold_boundary_exact_80_strong_match():
    """At exactly 80.0 with 0 missing required and no mismatch, verdict is Strong Match."""
    res = calculate_composite_score(
        {"score": 80.0, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 0.0},
        weights={"skills": 1.0, "experience": 0.0, "role": 0.0, "projects": 0.0},
    )

    assert res["overall_score"] == 80.0
    assert res["verdict"] == "Strong Match"


def test_threshold_boundary_79_9_moderate_match():
    """At 79.9 with otherwise clean criteria, verdict is Moderate Match."""
    res = calculate_composite_score(
        {"score": 79.9, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 0.0},
        weights={"skills": 1.0, "experience": 0.0, "role": 0.0, "projects": 0.0},
    )

    assert res["overall_score"] == 79.9
    assert res["verdict"] == "Moderate Match"


def test_threshold_boundary_exact_55_moderate_match():
    """At exactly 55.0, verdict is Moderate Match."""
    res = calculate_composite_score(
        {"score": 55.0, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 0.0},
        weights={"skills": 1.0, "experience": 0.0, "role": 0.0, "projects": 0.0},
    )

    assert res["overall_score"] == 55.0
    assert res["verdict"] == "Moderate Match"


def test_threshold_boundary_54_9_underqualified():
    """At 54.9, verdict is Underqualified."""
    res = calculate_composite_score(
        {"score": 54.9, "missing_required": []},
        {"score": 0.0},
        {"score": 0.0},
        {"score": 0.0},
        weights={"skills": 1.0, "experience": 0.0, "role": 0.0, "projects": 0.0},
    )

    assert res["overall_score"] == 54.9
    assert res["verdict"] == "Underqualified"


def test_reproducibility_identical_inputs_identical_outputs():
    """Verify determinism across 50 repeated executions with identical inputs."""
    skill_res = {"score": 87.5, "missing_required": ["Docker"], "flags": {}}
    exp_res = {"score": 75.0, "status": "underqualified", "gap_months": 6, "flags": {}}
    role_res = {"score": 100.0, "status": "match", "flags": {"role_mismatch": False}}
    proj_res = {"score": 66.7, "flags": {}}

    baseline = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    for _ in range(50):
        iteration = calculate_composite_score(skill_res, exp_res, role_res, proj_res)
        assert iteration == baseline
