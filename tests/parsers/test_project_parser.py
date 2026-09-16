from pathlib import Path

from src.parsers.project_parser import (
    process_projects,
)


def make_text_blocks(text: str) -> list[dict]:
    return [
        {
            "text": line.strip(),
            "bbox": (0, 0, 100, 10),
            "page": 0,
        }
        for line in text.splitlines()
        if line.strip()
    ]


# ============================================================
# Basic extraction
# ============================================================

def test_single_project():

    text = """
    PROJECTS:

    Bloger - A Full Stack Blog App | GitHub

    • Developed a scalable blog application
    • Features user authentication

    TECHNICAL SKILLS:
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == (
        "Bloger - A Full Stack Blog App | GitHub"
    )

    assert result[0]["description"] == [
        "• Developed a scalable blog application",
        "• Features user authentication",
    ]

    assert result[0]["metadata"] == []


def test_multiple_projects():

    text = """
    PROJECTS:

    Project Alpha
    • Built an application.

    Project Beta
    • Built an API.

    Project Gamma
    • Built a dashboard.

    TECHNICAL SKILLS:
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None
    assert len(result) == 3

    assert [
        project["project"]
        for project in result
    ] == [
        "Project Alpha",
        "Project Beta",
        "Project Gamma",
    ]


# ============================================================
# Wrapped descriptions
# ============================================================

def test_wrapped_description():

    text = """
    PROJECTS:

    Project Alpha

    • Built a scalable application using Python
      and FastAPI for backend services.

    TECHNICAL SKILLS:
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None

    assert result[0]["description"] == [
        "• Built a scalable application using Python "
        "and FastAPI for backend services."
    ]


def test_multiple_wrapped_descriptions():

    text = """
    PROJECTS:

    Project Alpha

    • Built backend services using Python
      and FastAPI.

    • Added authentication using JWT
      and OAuth.

    TECHNICAL SKILLS:
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None

    assert result[0]["description"] == [
        "• Built backend services using Python and FastAPI.",
        "• Added authentication using JWT and OAuth.",
    ]


# ============================================================
# Page boundary regression tests
# ============================================================

def test_project_continuation_across_page_boundary():

    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 200, 60),
            "page": 0,
        },
        {
            "text": "Project Alpha | GitHub",
            "bbox": (40, 100, 300, 115),
            "page": 0,
        },
        {
            "text": "• Built a full stack application using Python.",
            "bbox": (40, 120, 400, 135),
            "page": 0,
        },
        {
            "text": "HTML, CSS",
            "bbox": (40, 50, 200, 65),
            "page": 1,
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 100, 200, 110),
            "page": 1,
        },
    ]

    result = process_projects(
        text_blocks,
        [],
    )

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == "Project Alpha | GitHub"

    assert result[0]["description"] == [
        "• Built a full stack application using Python.",
    ]


def test_new_project_on_next_page_is_detected():

    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 200, 60),
            "page": 0,
        },
        {
            "text": "Project Alpha",
            "bbox": (40, 100, 250, 115),
            "page": 0,
        },
        {
            "text": "• Built an application.",
            "bbox": (40, 120, 300, 135),
            "page": 0,
        },
        {
            "text": "Project Beta",
            "bbox": (40, 50, 250, 65),
            "page": 1,
        },
        {
            "text": "• Built an API.",
            "bbox": (40, 70, 300, 85),
            "page": 1,
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 100, 200, 110),
            "page": 1,
        },
    ]

    result = process_projects(
        text_blocks,
        [],
    )

    assert result is not None
    assert len(result) == 2

    assert result[0]["project"] == "Project Alpha"
    assert result[1]["project"] == "Project Beta"


def test_ambiguous_page_boundary_text_is_not_appended():

    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 200, 60),
            "page": 0,
        },
        {
            "text": "Project Alpha",
            "bbox": (40, 100, 250, 115),
            "page": 0,
        },
        {
            "text": "• Built a web application.",
            "bbox": (40, 120, 300, 135),
            "page": 0,
        },
        {
            "text": "React, Node.js",
            "bbox": (40, 50, 250, 65),
            "page": 1,
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 100, 200, 110),
            "page": 1,
        },
    ]

    result = process_projects(
        text_blocks,
        [],
    )

    assert result is not None
    assert len(result) == 1

    assert result[0]["description"] == [
        "• Built a web application.",
    ]


# ============================================================
# Section termination
# ============================================================

def test_projects_stop_at_next_section():

    text = """
    PROJECTS:

    Project Alpha
    • Built an application.

    EDUCATION:

    Bachelor of Technology
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == "Project Alpha"


def test_empty_projects_section():

    text = """
    PROJECTS:

    EDUCATION:

    Bachelor of Technology
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is None


def test_no_projects_section():

    text = """
    EXPERIENCE:

    Software Engineer
    ABC Technologies

    EDUCATION:

    Bachelor of Technology
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is None


# ============================================================
# Metadata
# ============================================================

def test_project_metadata_is_preserved():

    text = """
    PROJECTS:

    Resume Intelligence Platform

    GitHub: https://github.com/example/project

    • Built a resume parser using Python.

    TECHNICAL SKILLS:
    """

    result = process_projects(
        make_text_blocks(text),
        [],
    )

    assert result is not None

    assert result[0]["metadata"] == [
        "GitHub: https://github.com/example/project"
    ]


# ============================================================
# Link association
# ============================================================

def test_project_link_association():

    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 200, 60),
            "page": 0,
        },
        {
            "text": "Project Alpha",
            "bbox": (40, 100, 250, 115),
            "page": 0,
        },
        {
            "text": "• Built an application.",
            "bbox": (40, 120, 300, 135),
            "page": 0,
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 150, 200, 160),
            "page": 0,
        },
    ]

    links = [
        {
            "url": "https://github.com/example/project",
            "bbox": (260, 100, 400, 115),
            "page": 0,
        }
    ]

    result = process_projects(
        text_blocks,
        links,
    )

    assert result is not None
    assert result[0]["metadata"] == [
        {
            "url": "https://github.com/example/project"
        }
    ]


def test_link_on_different_page_is_not_associated():

    text_blocks = [
        {
            "text": "PROJECTS:",
            "bbox": (20, 50, 200, 60),
            "page": 0,
        },
        {
            "text": "Project Alpha",
            "bbox": (40, 100, 250, 115),
            "page": 0,
        },
        {
            "text": "• Built an application.",
            "bbox": (40, 120, 300, 135),
            "page": 0,
        },
        {
            "text": "TECHNICAL SKILLS:",
            "bbox": (20, 150, 200, 160),
            "page": 0,
        },
    ]

    links = [
        {
            "url": "https://github.com/example/project",
            "bbox": (260, 100, 400, 115),
            "page": 1,
        }
    ]

    result = process_projects(
        text_blocks,
        links,
    )

    assert result is not None
    assert result[0]["metadata"] == []


# ============================================================
# Real resume regression
# ============================================================

def test_real_resume_projects():

    text = Path(
        "tests/fixtures/HARSHIT_WEBDEV.txt"
    ).read_text(
        encoding="utf-8"
    )

    text_blocks = make_text_blocks(text)

    result = process_projects(
        text_blocks,
        [],
    )

    assert result is not None
    assert len(result) >= 1

    for project in result:

        assert "project" in project
        assert "metadata" in project
        assert "description" in project

        assert project["project"] is not None
        assert isinstance(project["metadata"], list)
        assert isinstance(project["description"], list)