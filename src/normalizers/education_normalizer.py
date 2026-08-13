from ..configs.normalization_configs import DEGREE_ALIASES,FIELD_ALIASES
import re

def normalize_education(education: list[dict]) -> list[dict]:
    normalized_education = []

    for entry in education:
        normalized_entry = {
            "institution": entry.get("institution", "").strip(),
            "degree": None,
            "field":None,
            'start_year':None,
            "end_year":None,
            "score": None,
            "score_type": None,
        }

        start_year,end_year = normalize_duration(entry.get("duration"))
        degree,field = normalize_degree(entry.get("degree"))
        normalized_entry['start_year'] = start_year
        normalized_entry['end_year'] = end_year
        normalized_entry['degree'] = degree
        normalized_entry['field'] = field
        score = entry.get("cgpa")

        if score:
            score = score.strip()

            if score.lower().startswith("cgpa"):
                normalized_entry["score_type"] = "CGPA"
            elif score.lower().startswith("percentage"):
                normalized_entry["score_type"] = "percentage"

            value = score.split(":", 1)[-1].strip()

            try:
                normalized_entry["score"] = float(value)
            except ValueError:
                pass
        
        normalized_education.append(normalized_entry)
        
    return normalized_education

def normalize_degree(degree:str)->tuple[str|None,str|None]:
    degree = degree.strip()

    degree_lower = degree.lower()

    matched_degree =  None

    for alias,canonical in DEGREE_ALIASES.items():
        if degree_lower.startswith(alias):
            matched_degree = canonical
            degree_end = len(alias)
            break
    if matched_degree is None:
        return degree,None

    remainder = degree[degree_end:].strip()
    if remainder.startswith("in "):
       remainder = remainder[3:].strip()
    remainder = re.sub(r"^[\s,|:()\-]+","",remainder)
    remainder = remainder.strip("() ")

    if not remainder:
        return matched_degree,None
    field = FIELD_ALIASES.get(
        remainder.lower(),
        remainder
    )

    return matched_degree,field

def normalize_duration(duration:str)->tuple[int|None,int|None]:
    duration = duration.strip()
    years = re.findall(r'\d{4}',duration)
    years = [int(year) for year in years]
    if len(years) == 0:
        return (None,None)
    elif len(years) == 1:
        return (years[0],None)
    else:
        return (years[0],years[1])
