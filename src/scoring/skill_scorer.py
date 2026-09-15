def score_skills(skill_match: dict,skill_requirements: dict[str, str]) -> dict:
    shape = {
    "score": 0.0,
    "status": None,
    "earned_weight": 0,
    "resolved_max_weight": 0,
    "unknown_requirements": [],
    "breakdown": [] 
    }
    