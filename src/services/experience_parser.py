from ..configs.header_configs import SECTION_HEADERS,EXPERIENCE_HEADERS
from ..configs.experience_configs import ROLE_KEYWORDS,COMPANY_KEYWORDS
import re

def extract_experience(text:str)->list[list[str]]|None:
    lines = text.split("\n")
    inside_experience = False
    experience = []
    curr_experience = []

    for line in lines:
        line = line.strip()
        if not inside_experience:
            if any(header in line.upper() for header in EXPERIENCE_HEADERS):
                inside_experience = True
            continue
        if line.upper() in SECTION_HEADERS:
            break

        if line:
            if any(keyword in line.upper() for keyword in COMPANY_KEYWORDS):
              if curr_experience:
                 experience.append(curr_experience)
              curr_experience = []
            curr_experience.append(line)
    if curr_experience:
       experience.append(curr_experience)
    return experience if experience else None

def parse_experience(experience_block:list[list[str]])->list[dict]:
    parsed_experience = []

    for block in experience_block:

        experience = {
            "company":None,
            "duration":None,
            "role":None,
            "description":[]
        }
        for line in block:
            pattern = r"\d{4}\s*[-–]\s*(\d{4}|PRESENT)"
            if any(word in line.upper() for word in COMPANY_KEYWORDS):
               experience["company"] = line
            elif any(word in line.upper() for word in ROLE_KEYWORDS):
               experience["role"] = line
            elif re.search(pattern,line):
               experience["duration"] = line
            elif line.startswith(("•", "-", "*")):
               experience["description"].append(line)
        parsed_experience.append(experience)
    return parsed_experience if parsed_experience else None

def process_experience(text:str)->list[dict]|None:
    block = extract_experience(text)

    if not block:
        return None
    return parse_experience(block)