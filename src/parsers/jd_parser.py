import re

from ..configs.jd_configs import (
    ROLE_KEYWORDS,
    REQUIRED_SKILL_KEYWORDS,
    OPTIONAL_SKILL_KEYWORDS,
    NOISE_SECTION_HEADERS,
    JD_SECTION_HEADERS,
)
from ..configs.skill_configs import KNOWN_SKILLS
from ..parsers.skills_parser import (
    build_skill_patterns,
    is_skill_candidate,
    match_known_skill,
)


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
        \s+(?:of\s+)?experience
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


# ------------------------------------------------------
# Skill-section headers
# ------------------------------------------------------

SKILL_SECTION_HEADERS = {
    "required skills",
    "preferred skills",
    "nice to have",
    "technical skills",
    "skills",
}


# ------------------------------------------------------
# Words that must never become unknown skills
# ------------------------------------------------------

UNKNOWN_SKILL_STOPWORDS = {
    "experience",
    "experienced",
    "developer",
    "developers",
    "development",
    "engineer",
    "engineering",
    "knowledge",
    "required",
    "requirements",
    "strong",
    "skills",
    "skill",
    "using",
    "with",
    "and",
    "or",
    "is",
    "are",
    "the",
    "a",
    "an",
    "of",
    "in",
    "for",
    "on",
    "to",
    "we",
    "need",
    "needs",
    "have",
    "has",
    "build",
    "building",
    "mentioned",
    "here",
    "but",
    "should",
    "be",
    "ignored",
    "role",
    "position",
    "title",

    # Common JD role/domain words.
    "backend",
    "frontend",
    "fullstack",
    "full-stack",
    "software",
    "application",
    "applications",
    "product",
    "products",
    "technology",
    "technologies",
    "technical",
    "team",
    "teams",
    "candidate",
    "candidates",
}


# ------------------------------------------------------
# Raw JD extraction
# ------------------------------------------------------

def _extract_jd(text: str) -> list[str]:
    """
    Normalize raw JD text into non-empty stripped lines.
    """

    extracted_jd = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            extracted_jd.append(line)

    return extracted_jd


# ------------------------------------------------------
# Role extraction
# ------------------------------------------------------

def _extract_role(jd: list[str]) -> str | None:
    """
    Extract a role from configured role-keyword lines.

    Example:

        Job Title: Senior Backend / ML Engineer

    returns:

        Senior Backend / ML Engineer
    """

    for line in jd:
        if ":" not in line:
            continue

        key, role = line.split(":", 1)

        if key.strip().lower() not in ROLE_KEYWORDS:
            continue

        role = role.strip()

        for section in NOISE_SECTION_HEADERS | JD_SECTION_HEADERS:
            role = re.split(
                rf"\b{re.escape(section)}\b",
                role,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()

        return role or None

    return None


# ------------------------------------------------------
# Overall experience
# ------------------------------------------------------

def _extract_experience(jd: list[str]) -> int | None:
    """
    Extract overall professional/industry experience.

    Skill-specific experience is deliberately excluded.
    """

    text = " ".join(jd)

    match = re.search(
        YOE_PATTERN,
        text,
    )

    if not match:
        return None

    years = match.group(1) or match.group(2)

    if years is None:
        return None

    return int(years) * 12


# ------------------------------------------------------
# Skill-specific experience
# ------------------------------------------------------

def _extract_skill_specific_experience(
    jd: list[str],
) -> list[dict]:
    """
    Extract experience tied directly to a known skill.
    """

    skill_yoe = []

    for line in jd:
        for match in re.finditer(
            SKILL_YOE_PATTERN,
            line,
        ):
            years = (
                match.group("years_1")
                or match.group("years_2")
            )

            skill = (
                match.group("skill_1")
                or match.group("skill_2")
            )

            skill_yoe.append(
                {
                    "skill": skill,
                    "experience_months": int(years) * 12,
                }
            )

    return skill_yoe


# ------------------------------------------------------
# Noise-section filtering
# ------------------------------------------------------

def _filter_noise_sections(
    jd: list[str],
) -> list[str]:
    """
    Remove lines belonging to configured noise sections.

    Example:

        About the company
        We build amazing products.

    is removed until another JD section begins.
    """

    clean_jd = []
    noise_mode = False

    for line in jd:
        normalized_line = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized_line in NOISE_SECTION_HEADERS:
            noise_mode = True
            continue

        if noise_mode:
            if normalized_line in JD_SECTION_HEADERS:
                noise_mode = False
                clean_jd.append(line)

            continue

        clean_jd.append(line)

    return clean_jd


# ------------------------------------------------------
# Requirement classification
# ------------------------------------------------------

def _classify_skill_requirement(
    line: str,
) -> str:
    """
    Classify a JD line as required, optional, or unknown.
    """

    normalized_line = line.lower().strip()

    if any(
        keyword in normalized_line
        for keyword in REQUIRED_SKILL_KEYWORDS
    ):
        return "required"

    if any(
        keyword in normalized_line
        for keyword in OPTIONAL_SKILL_KEYWORDS
    ):
        return "optional"

    return "unknown"


# ------------------------------------------------------
# Section / role helpers
# ------------------------------------------------------

def _is_skill_section_header(line: str) -> bool:
    normalized = (
        line.strip()
        .rstrip(":")
        .lower()
    )

    return normalized in SKILL_SECTION_HEADERS


def _is_role_line(line: str) -> bool:
    """
    Prevent role/title metadata from being interpreted
    as an unknown skill.
    """

    if ":" not in line:
        return False

    key, _ = line.split(":", 1)

    return key.strip().lower() in ROLE_KEYWORDS


# ------------------------------------------------------
# Known skill overlap resolution
# ------------------------------------------------------

def _resolve_known_skill_matches(
    matches: list[dict],
) -> list[dict]:
    """
    Resolve overlapping known-skill matches.

    The longest overlapping match wins.
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
            previous["end"]
            - previous["start"]
        )

        current_length = (
            match["end"]
            - match["start"]
        )

        if current_length > previous_length:
            resolved[-1] = match

    return resolved


# ------------------------------------------------------
# Unknown skill extraction
# ------------------------------------------------------

def _extract_unknown_skill_matches(
    line: str,
    skill_patterns: list[tuple[str, re.Pattern]],
) -> list[dict]:
    """
    Extract conservative unknown technology-like skill candidates.

    Unknown skills may be:
        LangChain
        OpenTelemetry
        Jupyter
        FAISS
        NextGenAI

    Ordinary JD prose is filtered using UNKNOWN_SKILL_STOPWORDS.

    Known skills always take precedence, and derivatives such as
    Pythonic are rejected when Python is a configured known skill.
    """

    matches = []

    # --------------------------------------------------
    # Candidate pattern
    # --------------------------------------------------
    #
    # This intentionally allows normal capitalized technology
    # names such as:
    #
    #   Jupyter
    #   LangChain
    #   OpenTelemetry
    #   FAISS
    #
    # We do NOT require CamelCase anymore because legitimate
    # skills can be single capitalized words.
    #

    pattern = re.compile(
        r"""
        (?<!\w)
        [A-Z]
        [A-Za-z0-9]*
        (?:
            [-.]
            [A-Za-z0-9]+
        )*
        (?:[A-Z][a-z]+)*
        (?!\w)
        """,
        re.VERBOSE,
    )

    known_skill_names = [
        skill.casefold()
        for skill, _ in skill_patterns
    ]

    for match in pattern.finditer(line):
        candidate = match.group(0).strip()

        normalized = candidate.casefold()

        # --------------------------------------------------
        # Generic prose / JD words
        # --------------------------------------------------

        if normalized in UNKNOWN_SKILL_STOPWORDS:
            continue

        # --------------------------------------------------
        # Basic candidate validation
        # --------------------------------------------------

        if not is_skill_candidate(candidate):
            continue

        # --------------------------------------------------
        # Known skills always win
        # --------------------------------------------------

        if match_known_skill(
            candidate,
            skill_patterns,
        ):
            continue

        # --------------------------------------------------
        # Reject derivatives of known skills.
        #
        # Examples:
        #
        # Pythonic
        # PythonDeveloper
        #
        # But don't reject short known skills such as C.
        # --------------------------------------------------

        if any(
            normalized.startswith(skill)
            for skill in known_skill_names
            if len(skill) >= 4
        ):
            continue

        matches.append(
            {
                "skill": candidate,
                "start": match.start(),
                "end": match.end(),
                "known": False,
            }
        )

    return matches
# ------------------------------------------------------
# Complete JD skill extraction
# ------------------------------------------------------

def _extract_skills(jd: list[str]) -> list[str]:
    """
    Extract skills from JD text.

    Contract:
    - known skills use configured vocabulary names
    - matching is case-insensitive
    - unknown technology-like skills are preserved
    - output follows source order
    - duplicates are case-insensitive
    - overlapping known skills prefer the longest match
    - role/title metadata is not treated as a skill
    - section headers are not treated as skills
    """

    skill_patterns = build_skill_patterns()

    all_matches = []

    for line_number, raw_line in enumerate(jd):
        line = raw_line.strip()

        if not line:
            continue

        # Section headers are metadata, not skills.
        if _is_skill_section_header(line):
            continue

        # Role metadata is not a skill.
        if _is_role_line(line):
            continue

        # --------------------------------------------------
        # Known skills
        # --------------------------------------------------

        known_matches = []

        for skill, pattern in skill_patterns:
            for match in pattern.finditer(line):
                known_matches.append(
                    {
                        "skill": skill,
                        "start": match.start(),
                        "end": match.end(),
                        "known": True,
                    }
                )

        known_matches = _resolve_known_skill_matches(
            known_matches
        )

        # --------------------------------------------------
        # Unknown skills
        # --------------------------------------------------

        unknown_matches = _extract_unknown_skill_matches(
            line,
            skill_patterns,
        )

        # --------------------------------------------------
        # Known vocabulary always wins over unknown
        # candidates.
        # --------------------------------------------------

        filtered_unknown_matches = []

        for unknown in unknown_matches:
            overlaps_known = any(
                unknown["start"] < known["end"]
                and unknown["end"] > known["start"]
                for known in known_matches
            )

            if not overlaps_known:
                filtered_unknown_matches.append(
                    unknown
                )

        # --------------------------------------------------
        # Merge in source order
        # --------------------------------------------------

        line_matches = (
            known_matches
            + filtered_unknown_matches
        )

        line_matches.sort(
            key=lambda item: (
                item["start"],
                item["end"],
            )
        )

        for match in line_matches:
            all_matches.append(
                (
                    line_number,
                    match["start"],
                    match["skill"],
                )
            )

    # ------------------------------------------------------
    # Global ordering + case-insensitive deduplication
    # ------------------------------------------------------

    all_matches.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    seen = set()
    skills = []

    for _, _, skill in all_matches:
        key = skill.casefold()

        if key in seen:
            continue

        seen.add(key)
        skills.append(skill)

    return skills


# ------------------------------------------------------
# Generic overlap resolver
# ------------------------------------------------------

def _resolve_skill_overlaps(
    matches: list[dict],
) -> list[dict]:
    """
    Public/tested overlap resolver.

    Matches on different lines never overlap.
    """

    matches = sorted(
        matches,
        key=lambda item: (
            item["line"],
            item["start"],
            -(item["end"] - item["start"]),
        ),
    )

    resolved = []

    for match in matches:
        if not resolved:
            resolved.append(match)
            continue

        previous = resolved[-1]

        if (
            match["line"] != previous["line"]
            or match["start"] >= previous["end"]
        ):
            resolved.append(match)
            continue

        previous_length = (
            previous["end"]
            - previous["start"]
        )

        current_length = (
            match["end"]
            - match["start"]
        )

        if current_length > previous_length:
            resolved[-1] = match

    return resolved


# ------------------------------------------------------
# Public JD parser
# ------------------------------------------------------

def parse_jd(text: str) -> dict:
    """
    Parse a complete job description.

    Pipeline:

        raw text
            ↓
        line extraction
            ↓
        noise filtering
            ↓
        role / experience / skills
            ↓
        skill-specific experience
            ↓
        requirement classification
    """

    jd = _extract_jd(text)

    jd = _filter_noise_sections(jd)

    return {
        "role": _extract_role(jd),
        "experience_months": _extract_experience(jd),
        "skills": _extract_skills(jd),
        "skill_specific_experience": (
            _extract_skill_specific_experience(jd)
        ),
        "skill_requirements": [
            {
                "line": line,
                "requirement": _classify_skill_requirement(
                    line
                ),
            }
            for line in jd
        ],
    }