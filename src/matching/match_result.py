def compose_match_result(
    skill_match,
    experience_match,
    skill_experience_match,
    role_match
):
    return {
        "skill_match": skill_match,
        "experience_match": experience_match,
        "skill_experience_match": skill_experience_match,
        "role_match":role_match
    }