def match_project(projects: list[dict],jd_skills: list[str])->list[dict]:
    project_evidence = []
    for project in projects:
        evidence_entry = {
            "project" : project.get("project"),
            "metadata":project.get("metadata"),
            "demonstrated":[],
            "not_demonstrated":[]
        }
        data = project.get("description") or []
        for skill in jd_skills:
            found = any(skill.lower() in line.lower()
                for line in data)
            if found:
               evidence_entry["demonstrated"].append(skill)
            else:
                evidence_entry["not_demonstrated"].append(skill)
        project_evidence.append(evidence_entry)

    return project_evidence