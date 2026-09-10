from .resume_service import process_resume
from .jd_service import process_jd
from ..matching.skill_matcher import match_skills
from ..matching.role_matcher import match_roles
from ..matching.experience_matcher import (
    match_experience,
    match_skill_experience,
)
from ..matching.match_result import compose_match_result

async def match_resume_to_jd(resume_file, jd_input):
    resume_data = await process_resume(resume_file)
    jd_response = await process_jd(jd_input)

    jd_data = jd_response["jd"]

    return calculate_match(resume_data, jd_data)

def calculate_match(resume_data: dict,jd_data: dict) -> dict:

    skill_match = match_skills(resume_data['skills'],jd_data['skills'])

    experience_match = match_experience(resume_data["total_experience_months"],jd_data['experience_months'])

    skill_experience_match = match_skill_experience(resume_data['skill_experience'],jd_data['skill_specific_experience'])

    candidate_roles = [
    entry["position"]
    for entry in resume_data["experience"]
    if entry.get("position")] 

    target_role = jd_data['role']

    role_match = match_roles(candidate_roles,target_role)
    matched_resume_jd = compose_match_result(skill_match,experience_match,skill_experience_match,role_match)
    return matched_resume_jd