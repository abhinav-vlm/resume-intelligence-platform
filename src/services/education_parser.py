from ..configs.header_configs import SECTION_HEADERS,EDUCATION_SECTION_HEADERS
from ..configs.education_configs import INSTITUTION_KEYWORDS,DEGREE_KEYWORDS,MARKS
from ..utils.text_utils import is_duration,contains_keywords
import re

def extract_education(text:str)->list[list[str]]|None:
    lines = text.split("\n")
    education = []
    current_education = []
    inside_education = False

    for line in lines:
        line = line.strip()
        if not inside_education:
           if contains_keywords(line,EDUCATION_SECTION_HEADERS):
              inside_education = True
           continue
        if contains_keywords(line,SECTION_HEADERS):
            break
        if line:
           if contains_keywords(line,INSTITUTION_KEYWORDS):
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
         if contains_keywords(line,INSTITUTION_KEYWORDS):
            education["institution"] = line
         elif contains_keywords(line,DEGREE_KEYWORDS):
            education["degree"] = line
         elif is_duration(line):
            education["duration"] = line
         elif contains_keywords(line,MARKS):
            education["cgpa"] = line
      parsed_education.append(education)
   return parsed_education if parsed_education else None
         
def process_education(text:str)->list[dict]|None:
   blocks = extract_education(text)

   if not blocks:
      return None
   return parse_education(blocks)