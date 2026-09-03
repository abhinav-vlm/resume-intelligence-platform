def match_skills(resume_skills:list[str], jd_skills:list[str])->dict:
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)
    match = {
        "matched":[],
        "unmatched":[],
        "extra":[]
    }
    for skill in jd_skills:
        if skill in resume_set:
            match['matched'].append(skill)
        if skill not in resume_set:
            match['unmatched'].append(skill)

    for skill in resume_skills:
        if skill not in jd_set:
                match["extra"].append(skill)

    
    return match