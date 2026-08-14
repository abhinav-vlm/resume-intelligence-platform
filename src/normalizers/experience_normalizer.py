import re

def normalize_experience(experience:list[dict])->list[dict]:
    normalized_experience = []

    for entry in experience:
        normalize_entry = {
            "company": entry.get("company"),
            "start_month" : None,
            "end_month" : None,
            "start_year" : None,
            "end_year" : None,
            "position" : entry.get('role'),
            "description":entry.get('description') 
        }

        normalize_entry["start_month"], normalize_entry["end_month"], normalize_entry["start_year"], normalize_entry["end_year"] = _normalize_duration(entry.get("duration"))
        normalized_experience.append(normalize_entry)
    return normalized_experience

def _normalize_duration(duration:str)->tuple[str|None,str|None,int|None,int|None]:
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