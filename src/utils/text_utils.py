import re 
from ..configs.text_utils_configs import DURATION_PATTERNS

def is_duration(line:str)->bool:
    line = line.upper()

    return any(
        re.search(pattern,line) for pattern in DURATION_PATTERNS
    )

def contains_keywords(line:str,keywords:list[str])->bool:
    line = line.upper()

    return any(
        keyword in line for keyword in keywords
    )    

def _is_project_title(line:str)->bool:
    if not line:
        return False
    if line[0].islower():
        return False
    if line.endswith("."):
        return False
    if line.startswith(("•", "-", "*")):
        return False
    return True