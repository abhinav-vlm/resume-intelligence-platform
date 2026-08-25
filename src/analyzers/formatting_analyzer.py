from src.configs.header_configs import SECTION_HEADERS

def _analyze_bullet_formatting(entries: list[dict]) -> list[dict]:
    issues = []
    for index,entry in enumerate(entries):
        local_issue = {
            "index":index,
            "issues":[]
        }
        description = entry.get('description',[])
        if not description:
            issues.append(local_issue)
            continue
        first_bullet = _get_bullet_marker(description[0][0])

        for item in description:
            current_bullet = _get_bullet_marker(item)
            if current_bullet != first_bullet:
                local_issue["issues"].append("inconsistent_bullets")
                break
        issues.append(local_issue)
    return issues
def _analyze_section_headers(text: str) -> list[dict]:
    headers = []
    for line in text.splitlines():
        normalized_line = line.strip().rstrip(":").strip()
        if normalized_line.upper() in SECTION_HEADERS:
            headers.append({
                "header":normalized_line.upper(),
                'has_colon' : line.strip().endswith(":")})
    return headers

def _get_bullet_marker(item: str) -> str | None:
    if not item:
        return None

    if item.startswith(("•", "-", "*")):
        return item[0]

    return None

def _check_section_header_consistency(headers: list[dict]) -> list[dict]:
    header_consistency = []

    if not headers:
        return []

    expected_format = headers[0]["has_colon"]

    for header in headers:
        if header["has_colon"] != expected_format:
            header_consistency.append({
                "header": header["header"],
                "issue": "inconsistent_header_format",
            })

    return header_consistency

def analyze_formatting(resume: dict) -> dict:
    bullet_formatting = _analyze_bullet_formatting(
        resume["experience"] + resume["projects"]
    )

    section_headers = _analyze_section_headers(
        resume["text"]
    )
    section_header_consistency = _check_section_header_consistency(section_headers)
    return {
    "bullets": bullet_formatting,
    "section_headers": section_header_consistency,
      }