"""
Deterministic Match Scorer (Phase 5 Day 8).

Aggregates individual component match results (skills, overall experience,
skill-specific experience, role alignment, project demonstration) into a
reproducible 0–100 composite score with explicit dimension breakdown,
verdict engine, missing-data flags, and transparent human-readable explanation.
"""

from typing import Any

DEFAULT_WEIGHTS: dict[str, float] = {
    "skills": 0.40,
    "experience": 0.25,
    "role": 0.20,
    "projects": 0.15,
}

REQUIRED_SKILL_MULTIPLIER: float = 2.0
OPTIONAL_SKILL_MULTIPLIER: float = 1.0


def score_skills(
    skill_match: dict,
    skill_requirements: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Score candidate skills against JD skills.

    Differentiates required vs optional skills using weights:
      - Required: 2.0x weight
      - Optional: 1.0x weight
      - Default / Unspecified: 1.0x weight

    Handles empty candidate skills and empty JD skills explicitly.
    """
    matched = skill_match.get("matched", []) or []
    unmatched = skill_match.get("unmatched", []) or []
    total_jd_skills = len(matched) + len(unmatched)

    flags = {
        "candidate_skills_missing": len(matched) == 0 and total_jd_skills > 0,
        "jd_skills_missing": total_jd_skills == 0,
    }

    if total_jd_skills == 0:
        return {
            "score": 100.0,
            "matched_count": 0,
            "total_jd_skills": 0,
            "matched_required": [],
            "matched_optional": [],
            "missing_required": [],
            "missing_optional": [],
            "flags": flags,
        }

    # Build requirement lookup: skill.lower() -> requirement ("required" / "optional")
    req_map: dict[str, str] = {}
    if skill_requirements:
        for item in skill_requirements:
            s_name = item.get("skill")
            req = item.get("requirement")
            if s_name and req:
                req_map[s_name.lower()] = req.lower()

    matched_required: list[str] = []
    matched_optional: list[str] = []
    missing_required: list[str] = []
    missing_optional: list[str] = []

    earned_weight = 0.0
    total_weight = 0.0

    matched_set = set(matched)

    for skill in matched + unmatched:
        req = req_map.get(skill.lower(), "standard")
        w = (
            REQUIRED_SKILL_MULTIPLIER
            if req == "required"
            else OPTIONAL_SKILL_MULTIPLIER
        )
        total_weight += w

        if skill in matched_set:
            earned_weight += w
            if req == "required":
                matched_required.append(skill)
            else:
                matched_optional.append(skill)
        else:
            if req == "required":
                missing_required.append(skill)
            else:
                missing_optional.append(skill)

    if total_weight > 0:
        score = round((earned_weight / total_weight) * 100.0, 1)
    else:
        score = 0.0

    return {
        "score": score,
        "matched_count": len(matched),
        "total_jd_skills": total_jd_skills,
        "matched_required": matched_required,
        "matched_optional": matched_optional,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "flags": flags,
    }


def score_experience(
    experience_match: dict,
    skill_experience_match: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Score candidate experience against JD experience requirements.

    Meets tenure: 100.0.
    Underqualified: linear ratio min(1.0, candidate / required) * 100.
    Missing candidate experience: 0.0 with candidate_experience_missing flag.
    Missing JD experience requirement: 100.0 with jd_experience_unspecified flag.
    Underqualified in skill-specific experience: applies deduction.
    """
    status = experience_match.get("status", "unknown")
    required = experience_match.get("required")
    candidate = experience_match.get("candidate")
    gap_months = experience_match.get("difference", 0) or 0

    flags = {
        "candidate_experience_missing": candidate is None,
        "jd_experience_unspecified": required is None,
    }

    underqualified_skills: list[str] = []
    if skill_experience_match:
        for entry in skill_experience_match:
            if entry.get("status") == "underqualified":
                underqualified_skills.append(entry.get("skill", "Unknown"))

    if required is None:
        base_score = 100.0
    elif candidate is None:
        base_score = 0.0
    elif status == "meets":
        base_score = 100.0
    else:
        if required > 0:
            ratio = max(0.0, min(1.0, float(candidate) / float(required)))
            base_score = round(ratio * 100.0, 1)
        else:
            base_score = 100.0

    # Skill-specific tenure penalty (5 points per underqualified skill)
    penalty = len(underqualified_skills) * 5.0
    final_score = max(0.0, round(base_score - penalty, 1))

    return {
        "score": final_score,
        "status": status,
        "required_months": required,
        "candidate_months": candidate,
        "gap_months": gap_months if gap_months > 0 else 0,
        "underqualified_skills": underqualified_skills,
        "flags": flags,
    }


def score_role(role_match: dict) -> dict[str, Any]:
    """
    Score candidate role history against target job role.

    Match: 100.0.
    Unknown / unmapped: 50.0 (neutral) with role_unknown flag.
    Mismatch: 0.0 with role_mismatch flag.
    """
    status = role_match.get("status", "unknown")

    flags = {
        "role_mismatch": status == "mismatch",
        "role_unknown": status == "unknown",
    }

    if status == "match":
        score = 100.0
    elif status == "mismatch":
        score = 0.0
    else:
        score = 50.0

    return {
        "score": score,
        "status": status,
        "target_role": role_match.get("target_role"),
        "flags": flags,
    }


def score_projects(
    project_match: list[dict],
    jd_skills: list[str] | None = None,
) -> dict[str, Any]:
    """
    Score candidate project demonstrations against JD required skills.

    Evaluates the fraction of JD skills practically demonstrated in project descriptions.
    """
    jd_skills = jd_skills or []
    flags = {
        "no_project_evidence": len(project_match) == 0,
    }

    if not project_match:
        return {
            "score": 0.0,
            "demonstrated_skills": [],
            "flags": flags,
        }

    demonstrated_set: set[str] = set()
    for proj in project_match:
        for skill in proj.get("demonstrated", []) or []:
            demonstrated_set.add(skill)

    demonstrated_skills = sorted(list(demonstrated_set))

    if not jd_skills:
        score = 100.0
    else:
        score = round(
            min(100.0, (len(demonstrated_skills) / len(jd_skills)) * 100.0), 1
        )

    return {
        "score": score,
        "demonstrated_skills": demonstrated_skills,
        "flags": flags,
    }


def calculate_composite_score(
    skill_res: dict,
    exp_res: dict,
    role_res: dict,
    proj_res: dict,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Combine all dimensional scores into a normalized composite score (0–100)
    with human-readable verdict and explanations.
    """
    w = weights or DEFAULT_WEIGHTS

    w_skill = w.get("skills", 0.40)
    w_exp = w.get("experience", 0.25)
    w_role = w.get("role", 0.20)
    w_proj = w.get("projects", 0.15)

    s_score = skill_res.get("score", 0.0)
    e_score = exp_res.get("score", 0.0)
    r_score = role_res.get("score", 0.0)
    p_score = proj_res.get("score", 0.0)

    overall_score = round(
        (w_skill * s_score)
        + (w_exp * e_score)
        + (w_role * r_score)
        + (w_proj * p_score),
        1,
    )

    # Compile aggregated flags
    aggregated_flags: list[str] = []
    if skill_res.get("missing_required"):
        aggregated_flags.append(
            f"Missing required skills: {', '.join(skill_res['missing_required'])}"
        )
    if exp_res.get("gap_months", 0) > 0:
        aggregated_flags.append(
            f"Experience deficit: {exp_res['gap_months']} months"
        )
    if role_res.get("flags", {}).get("role_mismatch"):
        aggregated_flags.append("Role alignment mismatch")
    if proj_res.get("flags", {}).get("no_project_evidence"):
        aggregated_flags.append("No project evidence provided")

    # Verdict Engine
    # Strong Match: overall >= 80, role matched, no more than 1 missing required skill
    # Moderate Match: overall >= 55
    # Underqualified: overall < 55
    if (
        overall_score >= 80.0
        and len(skill_res.get("missing_required", [])) == 0
        and not role_res.get("flags", {}).get("role_mismatch")
    ):
        verdict = "Strong Match"
        explanation = (
            f"Candidate is a Strong Match ({overall_score}/100) meeting all critical "
            f"role, experience, and required skill criteria."
        )
    elif overall_score >= 55.0:
        verdict = "Moderate Match"
        explanation = (
            f"Candidate is a Moderate Match ({overall_score}/100) with relevant background, "
            f"but has some gaps: {'; '.join(aggregated_flags) if aggregated_flags else 'partial skill/project overlap'}."
        )
    else:
        verdict = "Underqualified"
        explanation = (
            f"Candidate is Underqualified ({overall_score}/100) due to significant deficits: "
            f"{'; '.join(aggregated_flags) if aggregated_flags else 'low composite alignment'}."
        )

    return {
        "overall_score": overall_score,
        "verdict": verdict,
        "breakdown": {
            "skills": s_score,
            "experience": e_score,
            "role": r_score,
            "projects": p_score,
        },
        "flags": aggregated_flags,
        "explanation": explanation,
    }
