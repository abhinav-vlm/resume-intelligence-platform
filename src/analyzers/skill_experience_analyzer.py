from src.utils.text_utils import contains_keywords
from src.utils.intervals import merge_intervals
from src.configs.duration_configs import MONTHS
from src.configs.normalization_configs import SKILL_ALIASES

def analyze_skill_experience(
    experience: list[dict],
    resume_skills: list[str]
) -> list[dict]:

    skill_experience = []

    for entry in experience:
        description = entry.get("description", [])

        for line in description:
            for skill in resume_skills:
                if (contains_keywords(line, [skill]) or any(contains_keywords(line, [alias]) 
                for alias, canonical in SKILL_ALIASES.items()
                    if canonical == skill )
                    ):
                    curr_entry = {
                        "skill": skill,
                        "evidence": {
                            "company": entry.get("company"),
                            "start_month": entry.get("start_month"),
                            "start_year": entry.get("start_year"),
                            "end_month": entry.get("end_month"),
                            "end_year": entry.get("end_year"),
                        }
                    }

                    skill_experience.append(curr_entry)

    return skill_experience

def calculate_skill_experience(skill_evidence: list[dict]) -> dict:
    skill_intervals = {}

    for entry in skill_evidence:
        skill = entry.get("skill")
        evidence = entry.get("evidence", {})

        end_month = MONTHS.get(evidence.get("end_month"))
        start_month = MONTHS.get(evidence.get("start_month"))
        end_year = evidence.get("end_year")
        start_year = evidence.get("start_year")

        # Skip evidence where dates are incomplete
        if None in (start_month, start_year, end_month, end_year):
            continue

        skill_interval = (
            (start_year, start_month),
            (end_year, end_month)
        )

        if skill not in skill_intervals:
            skill_intervals[skill] = {
                "intervals":[]
            }
        skill_intervals[skill]["intervals"].append(skill_interval)

    for skill, data in skill_intervals.items():
        intervals = data["intervals"]
        intervals.sort()
        merged_intervals = merge_intervals(intervals)
        data["intervals"] = merged_intervals
        data['experience_months'] = _calculate_months(merged_intervals)

    return skill_intervals


def _calculate_months(intervals: list[tuple]) -> int:
    months = 0
    for interval in intervals:
        month = interval[1][1] - interval[0][1]
        year = interval[1][0] - interval[0][0]
        months += month + year*12 +1
    return months

def process_skill_experience(
    experience: list[dict],
    resume_skills: list[str]
) -> dict:

    skill_evidence = analyze_skill_experience(
        experience,
        resume_skills
    )

    return calculate_skill_experience(skill_evidence)