from .resume_service import process_resume
from .jd_service import process_jd
from ..matching.skill_matcher import match_skills
from ..matching.role_matcher import match_roles
from ..matching.project_matcher import match_project
from ..matching.experience_matcher import (
    match_experience,
    match_skill_experience,
)
from ..matching.match_result import compose_match_result
from ..matching.scorer import (
    score_skills,
    score_experience,
    score_role,
    score_projects,
    calculate_composite_score,
)

async def match_resume_to_jd(resume_file, jd_input):
    resume_data = await process_resume(resume_file)
    jd_response = await process_jd(jd_input)

    jd_data = jd_response["jd"]

    return calculate_match(resume_data, jd_data)

def calculate_match(resume_data: dict, jd_data: dict) -> dict:
    resume_skills = resume_data.get("skills") or []
    unknown_skills = resume_data.get("unknown_skills") or []
    candidate_skills = list(dict.fromkeys(
            resume_skills + unknown_skills
            ))
    jd_skills = jd_data.get("skills") or []

    skill_match = match_skills(candidate_skills, jd_skills)

    experience_match = match_experience(
        resume_data.get("total_experience_months"),
        jd_data.get("experience_months")
    )

    skill_experience_match = match_skill_experience(
        resume_data.get("skill_experience") or {},
        jd_data.get("skill_specific_experience") or []
    )

    candidate_roles = [
        entry["position"]
        for entry in (resume_data.get("experience") or [])
        if entry.get("position")
    ]

    target_role = jd_data.get("role")

    role_match = match_roles(candidate_roles, target_role)

    project_match = match_project(
        resume_data.get("projects") or [],
        jd_skills
    )

    # Deterministic Scoring (P5D8)
    skill_res = score_skills(skill_match, jd_data.get("skill_requirements"))
    exp_res = score_experience(experience_match, skill_experience_match)
    role_res = score_role(role_match)
    proj_res = score_projects(project_match, jd_skills)

    scoring = calculate_composite_score(skill_res, exp_res, role_res, proj_res)

    matched_resume_jd = compose_match_result(
        skill_match,
        experience_match,
        skill_experience_match,
        role_match,
        project_match,
        scoring=scoring,
    )
    return matched_resume_jd