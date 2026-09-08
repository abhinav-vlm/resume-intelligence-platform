def match_experience(resume_experience: int | None,jd_experience: int | None) -> dict:
    match = {
        'required':jd_experience,
        'candidate':resume_experience,
        'difference':None,
        'status':"unknown"
    }
    if match["required"] is not None and match["candidate"] is not None:
       match["difference"] = match['required'] - match['candidate']
       if match["difference"] <= 0:
          match['status'] = "meets"
       else:
          match['status'] = "underqualified"
    return match

def match_skill_experience(
    jd_skill_experience: list[dict],
    resume_skill_experience: dict
) -> list[dict]:

    match = []

    for item in jd_skill_experience:
        entry = {
            "skill": item.get("skill"),
            "required_experience_months": item.get("experience") * 12,
            "candidate_experience_months": None,
            "difference_months": None,
            "status": None
        }

        skill = entry["skill"]

        if skill in resume_skill_experience:
            data = resume_skill_experience[skill]
            entry["candidate_experience_months"] = data["experience_months"]

        if (
            entry["required_experience_months"] is not None
            and entry["candidate_experience_months"] is not None
        ):
            entry["difference_months"] = (
                entry["required_experience_months"]
                - entry["candidate_experience_months"]
            )

            if entry["difference_months"] <= 0:
                entry["status"] = "meets"
            else:
                entry["status"] = "underqualified"
        else:
            entry["status"] = "unknown"

        match.append(entry)

    return match