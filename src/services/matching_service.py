from ..matching.skill_matcher import match_skills
from ..matching.experience_matcher import (
    match_experience,
    match_skill_experience,
)
from ..matching.match_result import compose_match_result

def match_resume_to_jd(resume_data: dict,jd_data: dict) -> dict:
    skill_match = match_skills(resume_data['skills'],jd_data['skills'])
    experience_match = match_experience(resume_data["total_experience_months"],jd_data['experience_months'])
    skill_experience_match = match_skill_experience(resume_data['skill_experience'],jd_data['skill_specific_experience'])
    
    matched_resume_jd = compose_match_result(skill_match,experience_match,skill_experience_match)
    return matched_resume_jd