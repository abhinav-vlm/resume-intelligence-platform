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


# Common bullet/list glyphs that may prefix skill lines (R-043).
_BULLET_PREFIX_RE = re.compile(r"^[\s\u2022\u2023\u25cf\u2043\u25e6\u25aa\u25b8\u25ba\u2192\u203a*\-–—]+")


def extract_skill_candidates(line: str) -> list[str]:
    """
    Split a structured skill line into candidates.

    Supported separators:
    - comma
    - pipe
    - conjunction 'and'
    - slash (excluding slashes inside known multi-token skills like CI/CD)

    R-043: Leading bullet glyphs (•, ‣, ●, -, *, –, →, ►, ▪, ▸, ◦) are
    stripped before any further processing so the first skill is not
    corrupted.

    R-045: Slash-containing known skills (e.g. CI/CD) are extracted from
    the raw value first.  Their character ranges are removed before the
    delimiter-split step so the slash does not fragment them.

    Multi-word skills remain intact.

    Examples::

        Python, React, SQL
        Python | C++ | JavaScript
        HTML, CSS and React JS
        • Python, React, SQL    ← bullet stripped
        CI/CD, Docker          ← CI/CD protected

    """

    # R-043: strip leading bullet glyph(s) and surrounding whitespace.
    line = _BULLET_PREFIX_RE.sub("", line).strip()

    if ":" in line:
        _, value = line.split(":", 1)
    else:
        value = line

    value = value.strip()

    # ------------------------------------------------------------------
    # R-045 / R-044: protect known skills containing delimiter characters
    # (slash or " and ") before splitting, so they are not fragmented.
    #
    # Examples:  CI/CD (slash)  /  Data Structures and Algorithms (and)
    #
    # For each such skill:
    #   1. Locate it in the working string (case-insensitive, word-bounded).
    #   2. Record the surface text.
    #   3. Replace its range with null-byte placeholders so the split
    #      regex cannot see the delimiter inside it.
    # ------------------------------------------------------------------
    protected_skills: list[str] = []
    protected_value = value

    # Sort longest first so more-specific compounds take precedence.
    for skill in sorted(KNOWN_SKILLS, key=len, reverse=True):
        if "/" not in skill and " and " not in skill.lower():
            continue
        pattern = re.compile(
            r"(?<![\w/])" + re.escape(skill) + r"(?![\w/])",
            re.IGNORECASE,
        )
        match = pattern.search(protected_value)
        if match:
            protected_skills.append(match.group(0))
            # Null-byte placeholder — preserves string length, invisible to split.
            protected_value = (
                protected_value[: match.start()]
                + "\x00" * (match.end() - match.start())
                + protected_value[match.end() :]
            )

    # Now split the protected value on regular delimiters.
    candidates = re.split(
        r"[,|/]|(?i:\s+and\s+)",
        protected_value,
    )

    result = [
        candidate.replace("\x00", "").strip()
        for candidate in candidates
        if candidate.replace("\x00", "").strip()
    ]

    # Re-insert the protected multi-delimiter skills.
    result.extend(protected_skills)

    return result


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