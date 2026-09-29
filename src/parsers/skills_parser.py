import re

from ..configs.header_configs import SKILL_CATEGORY_HEADERS
from ..configs.skill_configs import KNOWN_SKILLS
from ..configs.normalization_configs import SKILL_ALIASES


def build_skill_patterns() -> list[tuple[str, re.Pattern]]:
    """
    Build case-insensitive, boundary-aware patterns for all known skills
    and configured aliases.

    The returned skill name is the configured vocabulary entry.

    The regex match itself preserves the source surface form.
    """

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
    """
    Split a structured skill line into candidates.

    Supported separators:
    - comma
    - pipe
    - slash
    - conjunction 'and'

    Multi-word skills remain intact.

    Examples:

        Python, React, SQL
        Python | C++ | JavaScript
        HTML, CSS and React JS

    become:

        ["Python", "React", "SQL"]
        ["Python", "C++", "JavaScript"]
        ["HTML", "CSS", "React JS"]
    """

    if ":" in line:
        _, value = line.split(":", 1)
    else:
        value = line

    candidates = re.split(
        r"[,|/]|(?i:\s+and\s+)",
        value,
    )

    return [
        candidate.strip()
        for candidate in candidates
        if candidate.strip()
    ]


def _resolve_known_skill_matches(
    matches: list[dict],
) -> list[dict]:
    """
    Resolve overlapping known-skill matches.

    Longer matches win when they overlap.

    Examples:

        C++  vs C
        MySQL vs SQL
        React JS vs React

    The source surface form is preserved.
    """

    matches.sort(
        key=lambda item: (
            item["start"],
            -(item["end"] - item["start"]),
        )
    )

    resolved = []

    for match in matches:
        if not resolved:
            resolved.append(match)
            continue

        previous = resolved[-1]

        if match["start"] >= previous["end"]:
            resolved.append(match)
            continue

        previous_length = (
            previous["end"] - previous["start"]
        )

        current_length = (
            match["end"] - match["start"]
        )

        if current_length > previous_length:
            resolved[-1] = match

    return resolved


def extract_known_skills_from_line(
    line: str,
    skill_patterns: list[tuple[str, re.Pattern]],
) -> list[str]:
    """
    Extract known skills from arbitrary text.

    Matching is:
    - case-insensitive
    - boundary-aware
    - source-order preserving
    - overlap-aware

    Importantly, the returned value is the exact surface form appearing
    in the source text.

    Example:

        "Experience with PYTHON and ReactJS"

    returns:

        ["PYTHON", "ReactJS"]
    """

    matches = []

    for skill, pattern in skill_patterns:
        for match in pattern.finditer(line):
            matches.append(
                {
                    "skill": skill,
                    "start": match.start(),
                    "end": match.end(),
                    "surface": match.group(0),
                }
            )

    resolved = _resolve_known_skill_matches(matches)

    return [
        match["surface"]
        for match in resolved
    ]


def is_skill_candidate(candidate: str) -> bool:
    """
    Validate an unknown skill candidate.
    """

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
    """
    Return the configured known-skill representation when the complete
    candidate matches a known skill.

    Matching is case-insensitive.

    This function intentionally returns the configured vocabulary entry.
    The caller decides whether to preserve the source surface form.
    """

    candidate = candidate.strip()

    if not candidate:
        return None

    matches = []

    for skill, pattern in skill_patterns:
        if pattern.fullmatch(candidate):
            matches.append(skill)

    if not matches:
        return None

    return max(matches, key=len)


def add_unique_skill(
    skill: str,
    skills: list[str],
    seen: set[str],
) -> None:
    """
    Add a skill once using case-insensitive deduplication.

    The first source surface form wins.
    """

    key = skill.casefold()

    if key in seen:
        return

    skills.append(skill)
    seen.add(key)


def is_skill_category_header(line: str) -> bool:
    """
    Check whether a line is a configured skill-category header.
    """

    normalized = line.strip().rstrip(":").upper()

    return normalized in SKILL_CATEGORY_HEADERS


def _is_known_skill_in_text(
    candidate: str,
    skill_patterns: list[tuple[str, re.Pattern]],
) -> bool:
    """
    Return True when the complete candidate is a known skill.
    """

    return match_known_skill(
        candidate,
        skill_patterns,
    ) is not None


def extract_skills(text: str) -> dict[str, list[str]]:
    """
    Extract known and unknown skills from structured skill text.

    Contract:
    - known skills preserve their source surface form
    - unknown skills preserve their source surface form
    - matching is case-insensitive
    - duplicates are case-insensitive
    - first occurrence wins
    - known skills take precedence over unknown candidates
    - multi-word unknown skills are preserved
    """

    lines = text.split("\n")

    known_skills = []
    unknown_skills = []

    seen_known = set()
    seen_unknown = set()

    skill_patterns = build_skill_patterns()

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        if is_skill_category_header(line):
            continue

        candidates = extract_skill_candidates(line)

        for candidate in candidates:
            if not is_skill_candidate(candidate):
                continue

            known_skill = match_known_skill(
                candidate,
                skill_patterns,
            )

            if known_skill is not None:
                # IMPORTANT:
                # Preserve exactly what the user/source wrote.
                add_unique_skill(
                    candidate,
                    known_skills,
                    seen_known,
                )
                continue

            add_unique_skill(
                candidate,
                unknown_skills,
                seen_unknown,
            )

    return {
        "known": known_skills,
        "unknown": unknown_skills,
    }