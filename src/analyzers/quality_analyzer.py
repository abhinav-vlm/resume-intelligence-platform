import re

METRIC_PATTERN = re.compile(
    r"""
    \b\d+(?:\.\d+)?\s*%
    |
    \b\d+(?:\.\d+)?\s*percent\b
    |
    \b\d+(?:\.\d+)?\s*(?:x|ms|s|MB|GB|KB)\b
    |
    \b\d+(?:,\d{3})+(?:\+)?\b
    |
    \b\d+(?:\.\d+)?\s*[KMB]\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

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
        "experience": _analyze_experience_content(resume["experience"]),
        "projects": _analyze_projects_content(resume["projects"])
    }

def _analyze_consistency(resume: dict) -> dict:
    issues = []

    issues.extend(
        _analyze_education_consistency(resume["education"])
    )

    issues.extend(
        _analyze_experience_consistency(resume["experience"])
    )

    return {
        "issues": issues
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

def _analyze_experience_content(experience: list[dict]) -> list[dict]:
    
    analyzed_experience = []

    for index,entry in enumerate(experience):
        analyze_entry = {
            "index":index,
            "bullet_count":len(entry.get("description",[])),
            "content_length": sum(len(items) for items in entry.get("description",[])),
            "has_metrics":_has_metrics(entry.get("description",[]))
         }
        analyzed_experience.append(analyze_entry)
    return analyzed_experience

def _analyze_projects_content(projects: list[dict]) -> list[dict]:
    
    analyzed_projects = []
    
    for index,entry in enumerate(projects):
        analyze_entry = {
            "index":index,
            "bullet_count": len(entry.get("description",[])),
            "content_length": sum(len(items) for items in entry.get("description",[])),
            "has_metrics":_has_metrics(entry.get("description",[]))
         }
        analyzed_projects.append(analyze_entry)
    return analyzed_projects

def _has_metrics(description:list)->bool:
    for item in description:
        if METRIC_PATTERN.search(item):
           return True
    return False

def _analyze_education_consistency(education: list[dict]) -> list[dict]:
    education_consistency = []

    for index, entry in enumerate(education):
        if entry["start_year"] > entry["end_year"]:
            education_consistency.append({
                "section": "education",
                "index": index,
                "issue": "invalid_duration",
            })

    return education_consistency
def _analyze_experience_consistency(experience: list[dict]) -> list[dict]:
    experience_consistency = []

    for index, entry in enumerate(experience):
        if entry["start_year"] > entry["end_year"]:
            experience_consistency.append({
                "section": "experience",
                "index": index,
                "issue": "invalid_duration",
            })

    return experience_consistency