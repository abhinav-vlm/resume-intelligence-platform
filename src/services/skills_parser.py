from ..configs.header_configs import SECTION_HEADERS,SKILL

def extract_skills(text:str)->list[str]|None:
    lines = text.split('\n')

    skills = []
    inside_skills = False

    for line in lines:
        line = line.strip()

        if not inside_skills:
            if line.upper() in SKILL:
                inside_skills = True
            continue
        if line.upper() in SECTION_HEADERS:
            break
        if ':' in line:
            _,value = line.split(":",1)

            for skill in value.split(','):
                skill = skill.strip()
                if skill:
                    skills.append(skill)
    return skills if skills else None