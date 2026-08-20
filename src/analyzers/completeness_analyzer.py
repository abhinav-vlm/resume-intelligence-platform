from ..configs.analyzers_configs import REQUIREMENTS_TABLE

def analyze_completeness(resume:dict)->dict:
    analyzed_completeness = {
    "required": {},
    "recommended": {},
    "missing_required": [],
    "missing_recommended": [],
    }

    for category,fields in REQUIREMENTS_TABLE.items():
        for field in fields:
            present = bool(resume.get(field))
            analyzed_completeness[category][field] = present
            if not present:
                if category == "recommended":
                   analyzed_completeness['missing_recommended'].append(field)
                else:
                    analyzed_completeness['missing_required'].append(field)
    return analyzed_completeness