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
        "education": _analyze_education_structure(
            resume.get("education")
        ),
        "experience": _analyze_experience_structure(
            resume.get("experience")
        ),
        "projects": _analyze_projects_structure(
            resume.get("projects")
        ),
        "skills": _analyze_skills_structure(
            resume.get("skills")
        ),
    }


def _analyze_content(resume: dict) -> dict:
    return {
        "experience": _analyze_experience_content(
            resume.get("experience")
        ),
        "projects": _analyze_projects_content(
            resume.get("projects")
        ),
    }


def _analyze_consistency(resume: dict) -> dict:
    issues = []

    issues.extend(
        _analyze_education_consistency(
            resume.get("education")
        )
    )

    issues.extend(
        _analyze_experience_consistency(
            resume.get("experience")
        )
    )

    return {
        "issues": issues
    }


def _analyze_education_structure(
    education: list[dict] | None,
) -> list[dict]:

    if not education:
        return []

    final_entry = []

    required_fields = [
        "institution",
        "degree",
        "start_year",
        "end_year",
    ]

    for index, entry in enumerate(education):
        issues = {
            "index": index,
            "issues": [],
        }

        for item in required_fields:
            if entry.get(item) is None:
                issues["issues"].append(
                    f"missing_{item}"
                )

        final_entry.append(issues)

    return final_entry


def _analyze_experience_structure(
    experience: list[dict] | None,
) -> list[dict]:

    if not experience:
        return []

    final_entry = []

    required_fields = [
        "company",
        "position",
        "start_year",
        "end_year",
        "description",
    ]

    for index, entry in enumerate(experience):
        issues = {
            "index": index,
            "issues": [],
        }

        for item in required_fields:
            if entry.get(item) is None:
                issues["issues"].append(
                    f"missing_{item}"
                )

        final_entry.append(issues)

    return final_entry


def _analyze_projects_structure(
    projects: list[dict] | None,
) -> list[dict]:

    if not projects:
        return []

    final_entry = []

    required_fields = [
        "project",
        "description",
    ]

    for index, entry in enumerate(projects):
        issues = {
            "index": index,
            "issues": [],
        }

        for item in required_fields:
            if entry.get(item) is None:
                issues["issues"].append(
                    f"missing_{item}"
                )

        final_entry.append(issues)

    return final_entry


def _analyze_skills_structure(
    skills: list[str] | None,
) -> list[dict]:

    if not skills:
        return [{"issue": "missing_skills"}]

    return []


def _analyze_experience_content(
    experience: list[dict] | None,
) -> list[dict]:

    if not experience:
        return []

    analyzed_experience = []

    for index, entry in enumerate(experience):
        description = entry.get("description") or []

        analyzed_experience.append({
            "index": index,
            "bullet_count": len(description),
            "content_length": sum(
                len(item) for item in description
            ),
            "has_metrics": _has_metrics(description),
        })

    return analyzed_experience


def _analyze_projects_content(
    projects: list[dict] | None,
) -> list[dict]:

    if not projects:
        return []

    analyzed_projects = []

    for index, entry in enumerate(projects):
        description = entry.get("description") or []

        analyzed_projects.append({
            "index": index,
            "bullet_count": len(description),
            "content_length": sum(
                len(item) for item in description
            ),
            "has_metrics": _has_metrics(description),
        })

    return analyzed_projects


def _has_metrics(description: list[str]) -> bool:

    for item in description:
        if METRIC_PATTERN.search(item):
            return True

    return False


def _analyze_education_consistency(
    education: list[dict] | None,
) -> list[dict]:

    if not education:
        return []

    education_consistency = []

    for index, entry in enumerate(education):
        start_year = entry.get("start_year")
        end_year = entry.get("end_year")

        if (
            start_year is not None
            and end_year is not None
            and start_year > end_year
        ):
            education_consistency.append({
                "section": "education",
                "index": index,
                "issue": "invalid_duration",
            })

    return education_consistency


def _analyze_experience_consistency(
    experience: list[dict] | None,
) -> list[dict]:

    if not experience:
        return []

    experience_consistency = []

    for index, entry in enumerate(experience):
        start_year = entry.get("start_year")
        end_year = entry.get("end_year")

        if (
            start_year is not None
            and end_year is not None
            and start_year > end_year
        ):
            experience_consistency.append({
                "section": "experience",
                "index": index,
                "issue": "invalid_duration",
            })

    return experience_consistency