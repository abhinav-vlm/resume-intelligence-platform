from ..configs.normalization_configs import SKILL_ALIASES

def normalize_skills(skills:list[str])->list[str]:
    normalized_skills = []

    for skill in skills:
        skill = skill.strip()
        lookup_skill = skill.lower()

        canonical_skill = SKILL_ALIASES.get(lookup_skill,skill)

        if canonical_skill not in normalized_skills:
            normalized_skills.append(canonical_skill)
    return normalized_skills