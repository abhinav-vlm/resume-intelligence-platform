import re

from ..configs.jd_configs import (
    ROLE_KEYWORDS,
    REQUIRED_SKILL_KEYWORDS,
    OPTIONAL_SKILL_KEYWORDS,
    JD_SECTION_HEADERS,
    JD_SECTION_ALIASES,
    NOISE_SECTIONS,
)

from ..configs.skill_configs import KNOWN_SKILLS

from ..parsers.skills_parser import (
    build_skill_patterns,
    is_skill_candidate,
    match_known_skill,
)

from ..parsers.section_detector import detect_sections


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

    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


# ------------------------------------------------------
# JD section detection
# ------------------------------------------------------

def detect_jd_sections(text: str) -> list[dict]:
    """
    Detect and canonicalize JD sections.

    Uses the shared section detector rather than maintaining
    a separate JD-specific segmentation implementation.
    """

    return detect_sections(
        text,
        section_headers=JD_SECTION_HEADERS,
        section_aliases=JD_SECTION_ALIASES,
        prefix_matching=True,
    )


# ------------------------------------------------------
# Role extraction
# ------------------------------------------------------

def _extract_role(jd: list[str]) -> str | None:
    """
    Extract a role from configured role-keyword lines.
    """

    for line in jd:
        if ":" not in line:
            continue

        key, role = line.split(":", 1)

        if key.strip().lower() not in ROLE_KEYWORDS:
            continue

        role = role.strip()

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
# Noise filtering
# ------------------------------------------------------

def _filter_noise_sections(
    sections: list[dict],
) -> list[dict]:
    """
    Remove canonical noise sections.

    Filtering operates on already-segmented sections,
    making the operation re-entrant.

    A noise section therefore cannot permanently consume
    all following JD content.
    """

    return [
        section
        for section in sections
        if section["name"] not in NOISE_SECTIONS
    ]


# ------------------------------------------------------
# Requirement context
# ------------------------------------------------------

def _section_requirement_context(
    section_name: str | None,
) -> str:
    """
    Determine default requirement level from the parent section.
    """

    if section_name in {
        "REQUIREMENTS",
        "BASIC_QUALIFICATIONS",
        "MINIMUM_QUALIFICATIONS",
    }:
        return "required"

    if section_name in {
        "PREFERRED_QUALIFICATIONS",
        "BONUS",
        "DESIRED",
    }:
        return "optional"

    return "unknown"


# ------------------------------------------------------
# Requirement classification
# ------------------------------------------------------

def _classify_skill_requirement(
    line: str,
    parent_section: str | None = None,
) -> str:
    """
    Classify a JD line as required, optional, or unknown.

    Explicit line-level signals take precedence over the
    enclosing section context.
    """

    normalized_line = line.lower().strip()

    # Explicit required signals.
    if any(
        keyword in normalized_line
        for keyword in REQUIRED_SKILL_KEYWORDS
    ):
        return "required"

    # Explicit optional signals.
    if any(
        keyword in normalized_line
        for keyword in OPTIONAL_SKILL_KEYWORDS
    ):
        return "optional"

    # Inherit parent section context.
    return _section_requirement_context(
        parent_section
    )


# ------------------------------------------------------
# Section / role helpers
# ------------------------------------------------------

def _is_skill_section_header(line: str) -> bool:
    normalized = (
        line.strip()
        .rstrip(":")
        .lower()
    )

    return normalized in {
        "required skills",
        "preferred skills",
        "nice to have",
        "technical skills",
        "skills",
    }


def _is_role_line(line: str) -> bool:
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

    matches = []

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

        if normalized in UNKNOWN_SKILL_STOPWORDS:
            continue

        if not is_skill_candidate(candidate):
            continue

        if match_known_skill(
            candidate,
            skill_patterns,
        ):
            continue

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

def _extract_skills(
    sections: list[dict],
) -> tuple[list[str], list[dict]]:
    """
    Extract skills from structured JD sections.

    Returns:

        skills:
            Flat list of skill names.

        skill_requirements:
            Structured skill + requirement objects.
    """

    skill_patterns = build_skill_patterns()

    all_matches = []

    for section in sections:
        section_name = section["name"]

        # Noise should never contribute skills.
        if section_name in NOISE_SECTIONS:
            continue

        section_text = section["text"]

        for line_number, raw_line in enumerate(
            section_text.split("\n")
        ):
            line = raw_line.strip()

            if not line:
                continue

            if _is_skill_section_header(line):
                continue

            if _is_role_line(line):
                continue

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

            unknown_matches = (
                _extract_unknown_skill_matches(
                    line,
                    skill_patterns,
                )
            )

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

            requirement = _classify_skill_requirement(
                line,
                parent_section=section_name,
            )

            for match in line_matches:
                all_matches.append(
                    {
                        "line_number": line_number,
                        "start": match["start"],
                        "skill": match["skill"],
                        "requirement": requirement,
                    }
                )

    # Source order.
    all_matches.sort(
        key=lambda item: (
            item["line_number"],
            item["start"],
        )
    )

    seen = set()
    skills = []
    skill_requirements = []

    for match in all_matches:
        skill = match["skill"]
        key = skill.casefold()

        if key in seen:
            continue

        seen.add(key)

        skills.append(skill)

        skill_requirements.append(
            {
                "skill": skill,
                "requirement": match["requirement"],
            }
        )

    return skills, skill_requirements


# ------------------------------------------------------
# Generic overlap resolver
# ------------------------------------------------------

def _resolve_skill_overlaps(
    matches: list[dict],
) -> list[dict]:

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
        shared section detection
            ↓
        noise section removal
            ↓
        role / experience / skills
            ↓
        skill-specific experience
            ↓
        contextual requirement classification
    """

    jd = _extract_jd(text)

    # ----------------------------------------------
    # Section detection
    # ----------------------------------------------

    sections = detect_jd_sections(
        "\n".join(jd)
    )

    # ----------------------------------------------
    # Noise filtering
    # ----------------------------------------------

    clean_sections = _filter_noise_sections(
        sections
    )

    # ----------------------------------------------
    # Reconstruct valid JD lines
    # ----------------------------------------------

    clean_jd = []

    for section in clean_sections:
        if section["original_name"]:
            clean_jd.append(
                section["original_name"]
            )

        clean_jd.extend(
            line.strip()
            for line in section["text"].split("\n")
            if line.strip()
        )

    # ----------------------------------------------
    # Extraction
    # ----------------------------------------------

    skills, skill_requirements = _extract_skills(
        clean_sections
    )

    return {
        "role": _extract_role(clean_jd),

        "experience_months": _extract_experience(
            clean_jd
        ),

        "sections": clean_sections,

        "skills": skills,

        "skill_requirements": skill_requirements,

        "skill_specific_experience": (
            _extract_skill_specific_experience(
                clean_jd
            )
        ),
    }