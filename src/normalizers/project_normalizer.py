def normalize_projects(
    projects: list[dict],
) -> list[dict]:

    normalized_projects = []

    for entry in projects:
        normalized_entry = {
            "project": (entry.get("project") or "").strip(),
            "metadata": _normalize_metadata(
                entry.get("metadata") or []
            ),
            "description": entry.get("description") or [],
        }

        normalized_projects.append(normalized_entry)

    return normalized_projects


def _normalize_metadata(metadata: list) -> list[dict]:
    normalized_metadata = []

    for entry in metadata:

        # Link metadata
        if isinstance(entry, dict):
            url = entry.get("url")

            if not url:
                continue

            url = url.strip()

            if "github.com" in url.lower():
                metadata_type = "github"

            elif "linkedin.com" in url.lower():
                continue

            else:
                metadata_type = "website"

            normalized_metadata.append({
                "type": metadata_type,
                "url": url,
            })

        # Text metadata
        elif isinstance(entry, str):
            value = entry.strip()

            if value:
                normalized_metadata.append({
                    "type": "text",
                    "value": value,
                })

    return normalized_metadata