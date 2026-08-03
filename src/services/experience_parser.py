from ..configs.header_configs import SECTION_HEADERS,EXPERIENCE_HEADERS,COMPANY_KEYWORDS

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