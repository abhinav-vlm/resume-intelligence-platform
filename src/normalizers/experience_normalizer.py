import re

def normalize_experience(experience: list[dict]) -> list[dict]:
    normalized_experience = []

    for entry in experience:
        role = entry.get("role")

        normalize_entry = {
            "company": entry.get("company"),
            "start_month": None,
            "end_month": None,
            "start_year": None,
            "end_year": None,
            "position": _normalize_position(role),
            "employment_type": _normalize_employment_type(role),
            "description": entry.get("description"),
        }

        (
            normalize_entry["start_month"],
            normalize_entry["end_month"],
            normalize_entry["start_year"],
            normalize_entry["end_year"],
        ) = _normalize_duration(entry.get("duration"))

        normalized_experience.append(normalize_entry)

    return normalized_experience

def _normalize_duration(duration:str|None)->tuple[str|None,str|None,int|None,int|None]:
    if not duration:
        return None, None, None, None
    duration = duration.strip()
    months = re.findall(r"January|February|March|April|May|June|July|August|September|October|November|December",
      duration,
      re.IGNORECASE
    )
    years = re.findall(r'\d{4}',duration)
    years = [int(year) for year in years]
    month_count = len(months)
    year_count = len(years)
    if month_count == 0:
        months = (None,None)
    elif month_count == 1:
        months = (months[0],None)
    else:
        months = (months[0],months[1])

    if year_count == 0:
        years = (None,None)     
    elif year_count == 1 and month_count == 2:
        return (months[0],months[1],years[0],years[0])
    elif year_count == 1:
        years = (years[0],None)
    else:
        years = (years[0],years[1])

    final_duration = (months[0],months[1],years[0],years[1])
    return final_duration

def _normalize_employment_type(role: str) -> str | None:
    if not role:
        return None

    role_lower = role.lower()

    employment_types = {
        "intern": r"\bintern(ship)?\b",
        "contract": r"\b(contract|contractual)\b",
        "part-time": r"\bpart[-\s]?time\b",
        "full-time": r"\bfull[-\s]?time\b",
        "freelance": r"\bfreelance\b",
        "temporary": r"\btemporary\b",
        "apprentice": r"\bapprentice(ship)?\b",
        "trainee": r"\btrainee\b",
    }

    for employment_type, pattern in employment_types.items():
        if re.search(pattern, role_lower):
            return employment_type

    return None

def _normalize_position(role: str) -> str | None:
    if not role:
        return None

    position = re.sub(
        r"\b(remote|intern(ship)?|contract(ual)?|part[-\s]?time|full[-\s]?time|freelance|temporary|apprentice(ship)?|trainee)\b",
        "",
        role,
        flags=re.IGNORECASE
    )

    position = re.sub(r"\([^)]*\)", "", position)
    position = re.sub(r"\s+", " ", position).strip(" -,")

    return position or None