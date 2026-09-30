from src.configs.header_configs import SECTION_HEADERS, SECTION_ALIASES


def detect_sections(
    text: str,
    section_headers=None,
    section_aliases=None,
    prefix_matching: bool = False,
) -> list[dict]:
    """
    Generic section detector.

    Supports both resume and JD section detection.

    Args:
        text:
            Raw text to segment.

        section_headers:
            Collection of recognized normalized headers.
            Defaults to resume SECTION_HEADERS.

        section_aliases:
            Mapping of normalized headers -> canonical names.
            Defaults to resume SECTION_ALIASES.

        prefix_matching:
            When True, decorated headers such as:

                About Us - Our Story
                About the Company | Our Mission
                Requirements: What we're looking for

            may be recognized using configured header prefixes.

    Returns:
        List of section dictionaries:

        {
            "name": "skills",
            "original_name": "technical skills",
            "text": "Python\nAWS\n..."
        }
    """

    headers = (
        section_headers
        if section_headers is not None
        else SECTION_HEADERS
    )

    aliases = (
        section_aliases
        if section_aliases is not None
        else SECTION_ALIASES
    )

    normalized_headers = {
        normalize_header(header)
        for header in headers
    }

    sections = []
    current_section = None

    local_section = {
        "name": None,
        "original_name": None,
        "text": "",
    }

    lines = text.split("\n")

    for line in lines:
        normalized = normalize_header(line)

        if is_section_header(
            normalized,
            normalized_headers,
            prefix_matching=prefix_matching,
        ):
            # Flush the previous section.
            if current_section:
                sections.append(local_section)

            # Flush meaningful preamble.
            elif local_section["text"].strip():
                local_section["name"] = "preamble"
                sections.append(local_section)

            canonical_name = resolve_section_alias(
                normalized,
                aliases,
                prefix_matching=prefix_matching,
            )

            local_section = {
                "name": canonical_name,
                "original_name": normalized,
                "text": "",
            }

            current_section = canonical_name

        elif current_section:
            local_section["text"] += line + "\n"

        else:
            # Text before the first recognized section.
            local_section["text"] += line + "\n"

    # Flush EOF.
    if current_section:
        sections.append(local_section)

    elif local_section["text"].strip():
        local_section["name"] = "preamble"
        sections.append(local_section)

    return sections


def is_section_header(
    line: str,
    section_headers=None,
    prefix_matching: bool = False,
) -> bool:
    """
    Determine whether a normalized line is a section header.
    """

    normalized = normalize_header(line)

    headers = section_headers or SECTION_HEADERS

    normalized_headers = {
        normalize_header(header)
        for header in headers
    }

    if normalized in normalized_headers:
        return True

    if not prefix_matching:
        return False

    return any(
        normalized.startswith(header)
        and (
            normalized == header
            or normalized[len(header):].startswith(
                (" ", "-", "|", ":", "/")
            )
        )
        for header in normalized_headers
    )


def resolve_section_alias(
    normalized: str,
    aliases: dict,
    prefix_matching: bool = False,
) -> str:
    """
    Resolve a normalized section header to its canonical name.
    """

    if normalized in aliases:
        return aliases[normalized]

    if not prefix_matching:
        return normalized

    # Longest alias first prevents broad aliases from winning.
    candidates = sorted(
        aliases.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for alias, canonical in candidates:
        if normalized.startswith(alias) and (
            normalized == alias
            or normalized[len(alias):].startswith(
                (" ", "-", "|", ":", "/")
            )
        ):
            return canonical

    return normalized


def normalize_header(line: str) -> str:
    """
    Normalize section-header text.

    Example:

        "  Technical   Skills:  "
        -> "technical skills"
    """

    line = line.strip().lower()

    normalized_line = " ".join(
        line.split()
    )

    normalized_line = (
        normalized_line
        .rstrip(":")
        .strip()
    )

    return normalized_line