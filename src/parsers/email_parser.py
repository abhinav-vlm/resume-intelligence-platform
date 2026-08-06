import re

def extract_email(text:str)->str|None:
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern,text)

    if match:
        return match.group()
    return None