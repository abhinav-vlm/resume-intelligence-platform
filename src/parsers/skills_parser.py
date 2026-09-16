import re

from ..configs.header_configs import SECTION_HEADERS, SKILL,SKILL_CATEGORY_HEADERS
from ..configs.skill_configs import KNOWN_SKILLS
from ..configs.normalization_configs import SKILL_ALIASES
from ..utils.text_utils import contains_keywords


def build_skill_patterns() -> list[tuple[str, re.Pattern]]:
    skill_vocabulary = list(KNOWN_SKILLS) + list(SKILL_ALIASES.keys())

    return [
        (
            skill,
            re.compile(
                rf"(?<!\w){re.escape(skill)}(?!\w)",
                re.IGNORECASE,
            ),
        )
        for skill in skill_vocabulary
    ]


def extract_skill_candidates(line: str) -> list[str]:
    if ":" in line:
        _, value = line.split(":", 1)
    else:
        value = line

    return [
        candidate.strip()
        for candidate in re.split(r"[,|/]", value)
        if candidate.strip()
    ]


def is_skill_candidate(candidate: str) -> bool:
    candidate = candidate.strip()

    if not candidate:
        return False

    if len(candidate) > 60:
        return False

    if len(candidate.split()) > 6:
        return False

    return True


def match_known_skill(
    candidate: str,
    skill_patterns: list[tuple[str, re.Pattern]],
) -> str | None:

    for _, pattern in skill_patterns:
        match = pattern.fullmatch(candidate)

        if match:
            return match.group(0)

    return None


def add_unique_skill(
    skill: str,
    skills: list[str],
    seen: set[str],
) -> None:

    key = skill.lower()

    if key not in seen:
        skills.append(skill)
        seen.add(key)

def is_skill_category_header(line: str) -> bool:
    normalized = line.strip().rstrip(":").upper()
    return normalized in SKILL_CATEGORY_HEADERS

def extract_skills(text: str) -> dict[str, list[str]]:
    lines = text.split("\n")

    known_skills = []
    unknown_candidates = []

    seen_known = set()
    seen_unknown = set()

    skill_patterns = build_skill_patterns()

    inside_skills = False

    for line in lines:
        line = line.strip()
        if is_skill_category_header(line):
           continue
        if not line:
            continue

        if not inside_skills:
            if contains_keywords(line, SKILL):
                inside_skills = True
            continue

        if contains_keywords(line, SECTION_HEADERS):
            break

        candidates = extract_skill_candidates(line)

        for candidate in candidates:

            if not is_skill_candidate(candidate):
                continue

            known_skill = match_known_skill(
                candidate,
                skill_patterns,
            )

            if known_skill:
                add_unique_skill(
                    known_skill,
                    known_skills,
                    seen_known,
                )
            else:
                add_unique_skill(
                    candidate,
                    unknown_candidates,
                    seen_unknown,
                )

    return {
        "known": known_skills,
        "unknown": unknown_candidates,
    }