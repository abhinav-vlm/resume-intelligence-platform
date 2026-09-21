from src.configs.header_configs import SECTION_HEADERS, SECTION_ALIASES


def detect_sections(text: str) -> list[dict]:
    sections = []
    current_section = None

    local_section = {
        "name": None,
        "original_name": None,
        "text": ""
    }

    lines = text.split("\n")

    for line in lines:
        normalized = normalize_header(line)

        if is_section_header(normalized):

            # Flush the previous section before starting a new one.
            if current_section:
                sections.append(local_section)

            # If no section has started yet, flush meaningful preamble.
            elif local_section["text"].strip():
                local_section["name"] = "preamble"
                sections.append(local_section)

            # Convert the resume's heading into our canonical section name.
            canonical_name = SECTION_ALIASES.get(normalized, normalized)

            # Start the new section.
            local_section = {
                "name": canonical_name,
                "original_name": normalized,
                "text": ""
            }

            current_section = canonical_name

        elif current_section:
            # Preserve section content exactly as it appeared.
            local_section["text"] += line + "\n"

        else:
            # Still before the first section: collect preamble.
            local_section["text"] += line + "\n"

    # Flush whatever remains at EOF.
    if current_section:
        sections.append(local_section)

    elif local_section["text"].strip():
        # Resume contained text but no recognized sections.
        local_section["name"] = "preamble"
        sections.append(local_section)

    return sections


def is_section_header(line: str) -> bool:
    normalized = normalize_header(line)
    return normalized.upper() in SECTION_HEADERS


def normalize_header(line: str) -> str:
    line = line.strip().lower()
    normalized_line = " ".join(line.split())
    normalized_line = normalized_line.rstrip(":").strip()
    return normalized_line