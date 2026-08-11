from ..configs.header_configs import SECTION_HEADERS,EXPERIENCE_HEADERS
from ..configs.experience_configs import ROLE_KEYWORDS
from ..utils.text_utils import is_duration,contains_keywords
import re

def _extract_experience(text:str)->list[list[str]]|None:
    lines = text.split("\n")
    inside_experience = False
    experience = []
    curr_experience = []
    duration_found = False

    for i,line in enumerate(lines):
        line = line.strip()
        if not inside_experience:
            if contains_keywords(line,EXPERIENCE_HEADERS):
                inside_experience = True
            continue
        if contains_keywords(line,SECTION_HEADERS):
            break

        if line:
            if is_duration(line):
                if duration_found:
                    new_company = curr_experience.pop()
                    experience.append(curr_experience)
                    curr_experience = [new_company]
                else:
                    duration_found = True
            curr_experience.append(line)
    if curr_experience:
       experience.append(curr_experience)
    return experience if experience else None

def _parse_experience(experience_block:list[list[str]])->list[dict]:
    parsed_experience = []

    for block in experience_block:

        experience = {
            "company":None,
            "duration":None,
            "role":None,
            "description":[]
        }
        for i,line in enumerate(block):
            if contains_keywords(line,ROLE_KEYWORDS):
               experience["role"] = line
            elif is_duration(line):
               experience["duration"] = line
               experience["company"] = block[i-1]
            elif line.startswith(("•", "-", "*")):
               experience["description"].append(line)
        parsed_experience.append(experience)
    return parsed_experience if parsed_experience else None

def process_experience(text:str)->list[dict]|None:
    block = _extract_experience(text)

    if not block:
        return None
    return _parse_experience(block)