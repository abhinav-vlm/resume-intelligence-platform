def analyze_quality(resume: dict) -> dict:
    return {
        "structure": _analyze_structure(resume),
        "content": _analyze_content(resume),
        "consistency": _analyze_consistency(resume),
    }

def _analyze_structure(resume: dict) -> dict:
    return {
        "education": _analyze_education_structure(resume["education"]),
        "experience": _analyze_experience_structure(resume["experience"]),
        "projects": _analyze_projects_structure(resume["projects"]),
        "skills": _analyze_skills_structure(resume["skills"]),
    }
def _analyze_content(resume: dict) -> dict:
    return {
        "experience": [],
        "projects": [],
    }
def _analyze_consistency(resume: dict) -> dict:
    return {
        "issues": []
    }

def _analyze_education_structure(education: list[dict]) ->  list[dict]:
    final_entry = []
    required_fields = [
    "institution",
    "degree",
    "start_year",
    "end_year",
        ]
    for index,entry in enumerate(education):
        issues = {
                "index":index,
                "issues":[]
               }
        for item in required_fields:
            if entry.get(item) is None:
               issues["issues"].append(f"missing_{item}")
              
        final_entry.append(issues)
    return final_entry

def _analyze_experience_structure(experience:  list[dict]) ->  list[dict]:
    final_entry = []
    required_fields = [
    "company",
    "position",
    "start_year",
    "end_year",
    "description"
        ]
    for index,entry in enumerate(experience):
        issues = {
                "index":index,
                "issues":[]
               }
        for item in required_fields:
            if entry.get(item) is None:
               issues["issues"].append(f"missing_{item}")
        final_entry.append(issues)
    return final_entry
def _analyze_projects_structure(projects: list[dict]) ->  list[dict]:
    final_entry = []
    required_fields = [
    "project",
    "description"
        ]
    for index,entry in enumerate(projects):
        issues = {
                "index":index,
                "issues":[]
               }
        for item in required_fields:
            if entry.get(item) is None:
               issues["issues"].append(f"missing_{item}")
        final_entry.append(issues)
    return final_entry
def _analyze_skills_structure(skills: list[str]) -> list[dict]:
    if not skills:
        return [{"issue": "missing_skills"}]

    return []