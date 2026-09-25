import re

from ..configs.text_utils_configs import DURATION_PATTERNS


def is_duration(line: str) -> bool:
    line = line.upper().strip()

    if not line:
        return False

    return any(
        re.fullmatch(pattern, line)
        for pattern in DURATION_PATTERNS
    )

def contains_keywords(
    line: str,
    keywords: list[str],
) -> bool:

    line = line.upper()

    return any(
        re.search(
            rf"\b{re.escape(keyword.upper())}\b",
            line,
        )
        for keyword in keywords
    )


def _is_project_title(line: str) -> bool:

    if not line:
        return False

    line = line.strip()

    if line[0].islower():
        return False

    if line.endswith("."):
        return False

    if line.startswith(("•", "-", "*")):
        return False

    if is_duration(line):
        return False

    if "," in line:
        return False

    return True


def _is_likely_skill_list(line: str) -> bool:

    line = line.strip()

    if "," not in line:
        return False

    if line.endswith("."):
        return False

    candidates = [
        candidate.strip()
        for candidate in line.split(",")
        if candidate.strip()
    ]

    if len(candidates) < 2:
        return False

    return all(
        len(candidate.split()) <= 4
        and len(candidate) <= 40
        for candidate in candidates
    )


def _is_project_metadata(
    line: str,
    keywords: list[str],
) -> bool:

    return ":" in line and contains_keywords(
        line,
        keywords,
    )