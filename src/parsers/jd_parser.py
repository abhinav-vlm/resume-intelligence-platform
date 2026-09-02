import re
from ..configs.jd_configs import ROLE_KEYWORDS,REQUIRED_SKILL_KEYWORDS,OPTIONAL_SKILL_KEYWORDS,NOISE_SECTION_HEADERS,JD_SECTION_HEADERS
from ..configs.skill_configs import KNOWN_SKILLS

SKILL_PATTERN = "|".join(
    re.escape(skill)
    for skill in KNOWN_SKILLS
)

SKILL_YOE_PATTERN = re.compile(
    rf"""
    (?:
        (?P<years_1>\d+)\+?
        \s+(?:years?|yrs?)
        \s+(?:of\s+)?
        (?P<skill_1>{SKILL_PATTERN})
        \s+experience
    )
    |
    (?:
        (?P<years_2>\d+)\+?
        \s+(?:years?|yrs?)
        \s+of\s+experience
        \s+(?:with\s+)?
        (?P<skill_2>{SKILL_PATTERN})
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

YOE_PATTERN = re.compile(
    r"""
    \b(?:minimum|at\s+least)?\s*
    (\d+)\+?
    \s+(?:years?|yrs?)
    \s+(?:of\s+)?
    (?:professional\s+)?
    (?:industry\s+)?
    experience\b
    (?!\s+(?:with|in)\b)

    |

    \b(?:minimum|at\s+least)?\s*
    (\d+)\+?
    \s+(?:years?|yrs?)
    \s+(?:in\s+the\s+)?
    industry\b
    """,
    re.IGNORECASE | re.VERBOSE,
)

def _extract_jd(text:str)->list[str]:
    lines = text.split("\n")
    extracted_jd = []
    for line in lines:
        line = line.strip()
        if line:
           extracted_jd.append(line)
    return extracted_jd

def _extract_role(jd: list[str]) -> str | None:
    for line in jd:
        if ":" not in line:
            continue

        key, role = line.split(":", 1)

        if key.strip().lower() not in ROLE_KEYWORDS:
            continue

        role = role.strip()

        for section in NOISE_SECTION_HEADERS | JD_SECTION_HEADERS:
            pattern = rf"\b{re.escape(section)}\b"
            role = re.split(pattern, role, maxsplit=1, flags=re.IGNORECASE)[0]

        role = role.strip()

        return role or None

    return None

def _extract_experience(jd: list[str]) -> int | None:
    text = " ".join(jd)

    match = re.search(YOE_PATTERN, text)

    if not match:
        return None

    if match.group(1):
        return int(match.group(1))

    if match.group(2):
        return int(match.group(2))

    return None

def _extract_skill_specific_experience(jd: list[str]) -> list[dict]:
    skill_yoe = []

    for line in jd:
        matches = re.finditer(SKILL_YOE_PATTERN, line)

        for match in matches:
            years = match.group("years_1") or match.group("years_2")
            skill = match.group("skill_1") or match.group("skill_2")

            skill_yoe.append({
                "skill": skill,
                "experience": int(years),
            })

    return skill_yoe

def _filter_noise_sections(jd:list[str])->list[str]:
    clean_jd = []
    noise_mode = False
    for line in jd:
        normalized_line = line.lower().strip().rstrip(":")
        if normalized_line in NOISE_SECTION_HEADERS:
            noise_mode =True
            continue 
        if noise_mode:
           if normalized_line in JD_SECTION_HEADERS:
              noise_mode = False
              clean_jd.append(line)
           else:
              continue
        else:
            clean_jd.append(line)
    return clean_jd

def _classify_skill_requirement(line: str) -> str:
    normalized_line = line.lower().strip()

    if any(keyword in normalized_line for keyword in REQUIRED_SKILL_KEYWORDS):
        return "required"

    if any(keyword in normalized_line for keyword in OPTIONAL_SKILL_KEYWORDS):
        return "optional"

    return "unknown"

def _extract_skills(jd: list[str]) -> list[str]:
    seen = set()
    skills = []
    matches = []

    for line_index, line in enumerate(jd):
        for skill in KNOWN_SKILLS:
            pattern = re.compile(
                rf"(?<!\w){re.escape(skill)}(?!\w)",
                re.IGNORECASE,
            )
            match = pattern.search(line)

            if match:
                matches.append({
                     "skill": skill,
                     "line": line_index,
                     "start": match.start(),
                     "end": match.end(),
                               })
    matches.sort(key=lambda match: (match["line"], match["start"]))                          
    resolved = _resolve_skill_overlaps(matches)

    for match in resolved:
        skill = match["skill"]

        if skill not in seen:
              skills.append(skill)
              seen.add(skill)

    return skills

def _resolve_skill_overlaps(matches: list[dict]) -> list[dict]:
    resolved = []

    for match in matches:
        if not resolved:
            resolved.append(match)
            continue

        previous = resolved[-1]

        if (match["line"] != previous["line"] or match["start"] >= previous["end"]):
            resolved.append(match)
            continue

        previous_length = previous["end"] - previous["start"]
        current_length = match["end"] - match["start"]

        if current_length > previous_length:
            resolved[-1] = match

    return resolved
    
def parse_jd(text: str) -> dict:
    jd = _extract_jd(text)
    jd = _filter_noise_sections(jd)
    return {
        "role": _extract_role(jd),
        "experience": _extract_experience(jd),
        "skills": _extract_skills(jd),
        "skill_specific_experience":_extract_skill_specific_experience(jd),
        "skill_requirements": [
            {
                "line": line,
                "requirement": _classify_skill_requirement(line),
            }
            for line in jd
        ],
    }

