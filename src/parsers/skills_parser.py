import re

from ..configs.header_configs import SECTION_HEADERS, SKILL
from ..configs.skill_configs import KNOWN_SKILLS
from ..configs.normalization_configs import SKILL_ALIASES
from ..utils.text_utils import contains_keywords


def extract_skills(text: str) -> dict[str, list[str]]:
    lines = text.split("\n")

    known_skills = []
    unknown_candidates = []

    seen_known = set()
    seen_unknown = set()

    skill_vocabulary = list(KNOWN_SKILLS) + list(SKILL_ALIASES.keys())

    skill_patterns = [
        (
            skill,
            re.compile(
                rf"(?<!\w){re.escape(skill)}(?!\w)",
                re.IGNORECASE,
            ),
        )
        for skill in skill_vocabulary
    ]

    inside_skills = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if not inside_skills:
            if contains_keywords(line, SKILL):
                inside_skills = True
            continue

        if contains_keywords(line, SECTION_HEADERS):
            break

        # ---------------------------------------------------------
        # Extract individual skill candidates from this line
        # ---------------------------------------------------------

        if ":" in line:
            _, value = line.split(":", 1)
        else:
            value = line

        candidates = [
            candidate.strip()
            for candidate in value.split(",")
            if candidate.strip()
        ]

        for candidate in candidates:
            candidate_match = None

            for _, pattern in skill_patterns:
                match = pattern.fullmatch(candidate)

                if match:
                    candidate_match = match
                    break

            if candidate_match:
                surface_form = candidate_match.group(0)
                key = surface_form.lower()

                if key not in seen_known:
                    known_skills.append(surface_form)
                    seen_known.add(key)

            else:
                key = candidate.lower()

                if key not in seen_unknown:
                    unknown_candidates.append(candidate)
                    seen_unknown.add(key)

    return {
        "known": known_skills,
        "unknown": unknown_candidates,
    }