import re
from ..configs.jd_configs import ROLE_KEYWORDS,REQUIRED_SKILL_KEYWORDS,OPTIONAL_SKILL_KEYWORDS


YOE_PATTERN = re.compile(
     r"\b(?:minimum|at\s+least)?\s*(\d+)\+?\s+(?:years?|yrs?)\s+(?:of\s+)?(?:professional\s+)?(?:industry\s+)?experience\b"
     r"|\b(?:minimum|at\s+least)?\s*(\d+)\+?\s+(?:years?|yrs?)\s+(?:in\s+the\s+)?industry\b",
     re.IGNORECASE,
     )

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

def _extract_role(jd: list[str]) -> str | None:
    for line in jd:
        if ":" in line:
           key,role = line.split(":", 1)
           if key.strip().lower() in ROLE_KEYWORDS:
              return role.strip()
    return None

def _extract_experience(jd: list[str]) -> int | None:
    for line in jd:
        match = re.search(YOE_PATTERN, line)

        if not match:
            continue

        if match.group(1):
            return int(match.group(1))

        if match.group(2):
            return int(match.group(2))

    return None

def _classify_skill_requirement(line: str) -> str:
    normalized_line = line.lower().strip()

    if any(keyword in normalized_line for keyword in REQUIRED_SKILL_KEYWORDS):
        return "required"

    if any(keyword in normalized_line for keyword in OPTIONAL_SKILL_KEYWORDS):
        return "optional"

    return "unknown"

def parse_jd(text: str) -> dict:
    jd = _extract_jd(text)

    return {
        "role": _extract_role(jd),
        "experience": _extract_experience(jd),
        "skill_requirements": [
            {
                "line": line,
                "requirement": _classify_skill_requirement(line),
            }
            for line in jd
        ],
    }