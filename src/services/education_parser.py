from ..configs.header_configs import SECTION_HEADERS,EDUCATION_SECTION_HEADERS
from ..configs.education_configs import INSTITUTION_KEYWORDS,DEGREE_KEYWORDS,MARKS
import re

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
        if any(header in line.upper() for header in SECTION_HEADERS):
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
   
def parse_education(education_blocks:list[list[str]])->list[dict]:
   
   parsed_education = []
   for block in education_blocks:

      education = {
         "institution":None,
         "duration":None,
         "degree":None, 
         "cgpa":None
      }
      for line in block:
         pattern = r"\d{4}\s*[-–]\s*(\d{4}|PRESENT)"
         if any(word in line.upper() for word in INSTITUTION_KEYWORDS):
            education["institution"] = line
         elif any(word in line.upper() for word in DEGREE_KEYWORDS):
            education["degree"] = line
         elif re.search(pattern,line):
            education["duration"] = line
         elif any(word in line.upper() for word in MARKS):
            education["cgpa"] = line
      parsed_education.append(education)
   return parsed_education if parsed_education else None
         
def process_education(text:str)->list[dict]|None:
   blocks = extract_education(text)

   if not blocks:
      return None
   return parse_education(blocks)