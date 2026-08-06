import re

def extract_phone(text:str)->str|None:
    pattern = r"(\+91[\s-]?)?[6-9]\d{9}"

    match = re.search(pattern,text)

    if match:
        return match.group()
    return None