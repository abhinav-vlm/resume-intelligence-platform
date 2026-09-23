def extract_linkedin(links: list[dict]) -> str | None:
    for link in links:
        url = link.get("url", "").lower()

        if "linkedin.com/" in url:
            return link["url"]

    return None