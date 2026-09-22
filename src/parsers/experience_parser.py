from ..configs.experience_configs import ROLE_KEYWORDS
from ..utils.text_utils import is_duration, contains_keywords

def _extract_experience(text: str) -> list[list[str]] | None:
    lines = text.split("\n")
    experience = []
    curr_experience = []
    duration_found = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

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
        description_started = False
        for i,line in enumerate(block):
            if contains_keywords(line,ROLE_KEYWORDS):
               experience["role"] = line
               description_started = False
            elif is_duration(line):
               experience["duration"] = line
               experience["company"] = block[i-1]
               description_started = False
            elif line.startswith(("•", "-", "*")):
               experience["description"].append(line)
               description_started = True
            elif description_started:
                experience["description"][-1] += " " + line
        parsed_experience.append(experience)
    return parsed_experience if parsed_experience else None

def process_experience(text:str)->list[dict]|None:
    block = _extract_experience(text)

    if not block:
        return None
    return _parse_experience(block)