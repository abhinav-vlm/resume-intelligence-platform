from pathlib import Path

from src.parsers.pdf_parser import extract_links, extract_text_blocks


PDF_PATH = Path("tests/fixtures/HARSHIT_WEBDEV.pdf")


def test_extract_text_blocks():
    content = PDF_PATH.read_bytes()

    result = extract_text_blocks(content)

    assert result
    assert isinstance(result, list)

    block = result[0]

    assert "text" in block
    assert "bbox" in block
    assert "page" in block

    assert isinstance(block["text"], str)
    assert isinstance(block["bbox"], tuple)
    assert len(block["bbox"]) == 4
    assert isinstance(block["page"], int)


def test_extract_links():
    content = PDF_PATH.read_bytes()

    result = extract_links(content)

    assert result
    assert isinstance(result, list)

    link = result[0]

    assert "url" in link
    assert "bbox" in link
    assert "page" in link

    assert link["url"].startswith("https://")
    assert isinstance(link["bbox"], tuple)
    assert len(link["bbox"]) == 4
    assert isinstance(link["page"], int)


def test_extract_project_links():
    content = PDF_PATH.read_bytes()

    result = extract_links(content)

    urls = [link["url"] for link in result]

    assert "https://github.com/Blockmecoder/Bloger" in urls
    assert "https://github.com/Blockmecoder/CITY_APP" in urls
    assert "https://github.com/Blockmecoder/PrompTopic" in urls

def make_text_blocks(text: str) -> list[dict]:
    return [
        {
            "text": line.strip(),
            "bbox": (0, 0, 100, 10),
            "page": 0
        }
        for line in text.splitlines()
        if line.strip()
    ]

from src.parsers.project_parser import process_projects


def make_text_blocks(text: str) -> list[dict]:
    return [
        {
            "text": line.strip(),
            "bbox": (0, 0, 100, 10),
            "page": 0
        }
        for line in text.splitlines()
        if line.strip()
    ]


def test_single_project():
    text = """
    PROJECTS:
    Bloger - A Full Stack Blog App | GitHub
    • Developed a scalable blog application
    • Features user authentication
    TECHNICAL SKILLS:
    """

    result = process_projects(make_text_blocks(text), [])

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == "Bloger - A Full Stack Blog App | GitHub"

    assert result[0]["description"] == [
        "• Developed a scalable blog application",
        "• Features user authentication"
    ]

    assert result[0]["metadata"] == []

def test_wrapped_description():
    text = """
    PROJECTS:
    Bloger - A Full Stack Blog App | GitHub
    • Developed a scalable application enabling users to create and
    explore blogs with 15 percent more efficiency.
    • Features user authentication.
    TECHNICAL SKILLS:
    """

    result = process_projects(make_text_blocks(text), [])

    assert result is not None

    assert result[0]["description"] == [
        "• Developed a scalable application enabling users to create and explore blogs with 15 percent more efficiency.",
        "• Features user authentication."
    ]

def test_multiple_projects():
    text = """
    PROJECTS:
    Project Alpha | GitHub
    • Built an application.
    • Added authentication.

    Project Beta | GitHub
    • Built an API.
    • Added database integration.

    Project Gamma
    • Built a dashboard.

    TECHNICAL SKILLS:
    """

    result = process_projects(make_text_blocks(text), [])

    assert result is not None
    assert len(result) == 3

    assert result[0]["project"] == "Project Alpha | GitHub"
    assert result[1]["project"] == "Project Beta | GitHub"
    assert result[2]["project"] == "Project Gamma"

def test_no_projects():
    text = """
    EDUCATION:
    National Institute of Technology

    EXPERIENCE:
    Software Engineer

    TECHNICAL SKILLS:
    Python
    """

    result = process_projects(make_text_blocks(text), [])

    assert result is None

def test_empty_projects_section():
    text = """
    PROJECTS:

    TECHNICAL SKILLS:
    Python
    """

    result = process_projects(make_text_blocks(text), [])

    assert result is None

def test_project_link_association():
    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 100, 60),
            "page": 0
        },
        {
            "text": "Project Alpha | GitHub",
            "bbox": (40, 100, 250, 115),
            "page": 0
        },
        {
            "text": "• Built an application.",
            "bbox": (40, 120, 300, 135),
            "page": 0
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 150, 150, 160),
            "page": 0
        }
    ]

    links = [
        {
            "url": "https://github.com/example",
            "bbox": (200, 100, 250, 115),
            "page": 0
        }
    ]

    result = process_projects(text_blocks, links)

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == "Project Alpha | GitHub"

    assert result[0]["metadata"] == [
        {
            "url": "https://github.com/example"
        }
    ]

from pathlib import Path

from src.parsers.pdf_parser import extract_text_blocks, extract_links
from src.parsers.project_parser import process_projects


def test_real_resume_projects():
    pdf_path = Path("tests/fixtures/HARSHIT_WEBDEV.pdf")
    content = pdf_path.read_bytes()

    text_blocks = extract_text_blocks(content)
    links = extract_links(content)

    result = process_projects(text_blocks, links)

    assert result is not None
    assert len(result) == 3

    assert result[0]["project"] == "Bloger - A Full Stack Blog App | GitHub"
    assert result[1]["project"] == "Weather Sphere - A Real-time Weather App | GitHub"
    assert result[2]["project"] == "PrompTopic - An AI Prompting Tool | GitHub"

    assert result[0]["metadata"] == [
        {"url": "https://github.com/Blockmecoder/Bloger"}
    ]

    assert result[1]["metadata"] == [
        {"url": "https://github.com/Blockmecoder/CITY_APP"}
    ]

    assert result[2]["metadata"] == [
        {"url": "https://github.com/Blockmecoder/PrompTopic"}
    ]

