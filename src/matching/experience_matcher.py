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

def match_skill_experience(jd_skill_experience:list[dict],resume_skill_experience:list[dict])->list[dict]:
    match = []
    for item in jd_skill_experience:
        entry = {
            'skill' : item.get("skill"),
            'required_experience':
        }