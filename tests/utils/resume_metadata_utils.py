from src.utils.resume_metadata_utils import extract_linkedin


def test_extract_linkedin_returns_linkedin_url():
    links = [
        {
            "url": "https://github.com/user",
            "bbox": (),
            "page": 0,
        },
        {
            "url": "https://www.linkedin.com/in/test-user",
            "bbox": (),
            "page": 0,
        },
    ]

    result = extract_linkedin(links)

    assert result == "https://www.linkedin.com/in/test-user"


def test_extract_linkedin_returns_none_when_missing():
    links = [
        {
            "url": "https://github.com/user",
            "bbox": (),
            "page": 0,
        },
        {
            "url": "https://example.com",
            "bbox": (),
            "page": 0,
        },
    ]

    assert extract_linkedin(links) is None


def test_extract_linkedin_is_case_insensitive():
    links = [
        {
            "url": "https://WWW.LINKEDIN.COM/in/test-user",
            "bbox": (),
            "page": 0,
        }
    ]

    assert extract_linkedin(links) == (
        "https://WWW.LINKEDIN.COM/in/test-user"
    )


def test_extract_linkedin_returns_first_linkedin_url():
    links = [
        {
            "url": "https://linkedin.com/in/first",
            "bbox": (),
            "page": 0,
        },
        {
            "url": "https://linkedin.com/in/second",
            "bbox": (),
            "page": 0,
        },
    ]

    assert extract_linkedin(links) == (
        "https://linkedin.com/in/first"
    )