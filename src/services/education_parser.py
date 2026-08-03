from ..configs.header_configs import SECTION_HEADERS,EDUCATION_SECTION_HEADERS,INSTITUTION_KEYWORDS

def extract_education(text:str)->list[list[str]]|None:
    lines = text.split("\n")
    education = []
    current_education = []
    inside_education = False

    for line in lines:
        line = line.strip()
        if not inside_education:
           if any(header in line.upper() for header in EDUCATION_SECTION_HEADERS):
              inside_education = True
           continue
        if line.upper() in SECTION_HEADERS:
            break
        if line:
           if any(keyword in line.upper() for keyword in INSTITUTION_KEYWORDS):
              if current_education:
                education.append(current_education)
              current_education = []
           current_education.append(line)
    if current_education:
       education.append(current_education)
           
    return education if education else None