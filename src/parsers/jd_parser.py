
def _extract_jd(text:str)->list[str]:
    lines = text.split("\n")
    extracted_jd = []
    for line in lines:
        line = line.strip()
        if line:
           extracted_jd.append(line)
    return extracted_jd

def _parse_jd(jd:list[dict])->list[dict]:
    parsed_jd = []
    for entry in jd:
        entry_jd = {
            'role': None,
            "experience":None
        }
    return jd

def parse_jd(text: str) -> list[str]:
    jd = _extract_jd(text)
    return jd