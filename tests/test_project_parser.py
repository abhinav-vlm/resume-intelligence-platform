from src.parsers.project_parser import process_projects
from pathlib import Path

def test_process_projects():
    text = """
    PROJECTS:
    Bloger - A Full Stack Blog App | GitHub
    • Developed a scalable blog application 
    • Features user authentication
    TECHNICAL SKILLS:
    • Python
    """

    result = process_projects(text)
    assert result is not None
    assert len(result) == 1

    assert result[0]['project'] == 'Bloger - A Full Stack Blog App | GitHub'
    assert result[0]['description'] == [
        '• Developed a scalable blog application',
    '• Features user authentication'
    ]


def test_bullet_with_metadata_keyword_is_description():
    text = """
    PROJECTS :
    Weather Sphere - A Real-time Weather App | GitHub
    • Developed a real-time dynamic website displaying current weather conditions.
    • Utilizes OpenWeather API for fetching weather reports.
    TECHNICAL SKILLS :
    """

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1

    project = result[0]

    assert project["project"] == "Weather Sphere - A Real-time Weather App | GitHub"
    assert project["metadata"] == []

    assert project["description"] == [
        "• Developed a real-time dynamic website displaying current weather conditions.",
        "• Utilizes OpenWeather API for fetching weather reports."
    ]

def test_wrapped_description_line():
    text = """
    PROJECTS :
    Bloger - A Full Stack Blog App | GitHub
    • Developed a scalable application enabling users to create and
    explore blogs with 15 percent more efficiency.
    • Features user authentication.
    TECHNICAL SKILLS :
    """

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1

    project = result[0]

    assert project["project"] == "Bloger - A Full Stack Blog App | GitHub"

    assert project["description"] == [
        "• Developed a scalable application enabling users to create and explore blogs with 15 percent more efficiency.",
        "• Features user authentication."
    ]

def test_multiple_projects():
    text = """
    PROJECTS :
    Project Alpha | GitHub
    • Built an application.
    • Added authentication.

    Project Beta | GitHub
    • Built an API.
    • Added database integration.

    Project Gamma
    • Built a dashboard.

    TECHNICAL SKILLS :
    """

    result = process_projects(text)

    assert result is not None
    assert len(result) == 3

    assert result[0]["project"] == "Project Alpha | GitHub"
    assert result[0]["description"] == [
        "• Built an application.",
        "• Added authentication."
    ]

    assert result[1]["project"] == "Project Beta | GitHub"
    assert result[1]["description"] == [
        "• Built an API.",
        "• Added database integration."
    ]

    assert result[2]["project"] == "Project Gamma"
    assert result[2]["description"] == [
        "• Built a dashboard."
    ]

def test_project_metadata():
    text = """
    PROJECTS :
    Project Alpha
    GitHub: github.com/example
    Live Demo: example.com
    • Built an application.
    • Added authentication.

    TECHNICAL SKILLS :
    """

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1

    project = result[0]

    assert project["project"] == "Project Alpha"

    assert project["metadata"] == [
        "GitHub: github.com/example",
        "Live Demo: example.com"
    ]

    assert project["description"] == [
        "• Built an application.",
        "• Added authentication."
    ]

def test_no_projects():
    text = """
    EDUCATION :
    National Institute of Technology

    EXPERIENCE :
    Software Engineer

    TECHNICAL SKILLS :
    Python
    """

    result = process_projects(text)

    assert result is None

def test_empty_projects_section():
    text = """
    PROJECTS :

    TECHNICAL SKILLS :
    Python
    """

    result = process_projects(text)

    assert result is None

def test_project_title_only():
    text = '''
    PROJECTS
    Project Alpha | GitHub

    TECHNICAL SKILLS
    '''

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["project"] == "Project Alpha | GitHub"
    assert result[0]["metadata"] == []
    assert result[0]["description"] == []

def test_project_metadata_only():
    text = """
PROJECTS
Project Alpha | GitHub
Live Demo: example.com

TECHNICAL SKILLS
"""

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1
    assert result[0]["project"] == "Project Alpha | GitHub"
    assert result[0]["metadata"] == ["Live Demo: example.com"]
    assert result[0]["description"] == []

def test_project_metadata_and_description():
    text = """
PROJECTS
Project Alpha | GitHub
Live Demo: example.com
• Built an application.
• Added authentication.

TECHNICAL SKILLS
"""

    result = process_projects(text)

    assert result is not None
    assert len(result) == 1

    assert result[0]["project"] == "Project Alpha | GitHub"
    assert result[0]["metadata"] == ["Live Demo: example.com"]
    assert result[0]["description"] == [
        "• Built an application.",
        "• Added authentication.",
    ]

def test_real_resume_projects():
    text = Path("tests/fixtures/HARSHIT_WEBDEV.txt").read_text(
        encoding="utf-8"
    )

    result = process_projects(text)

    assert result is not None
    assert len(result) == 3

    assert result[0]["project"] == "Bloger - A Full Stack Blog App | GitHub"
    assert result[1]["project"] == "Weather Sphere - A Real-time Weather App | GitHub"
    assert result[2]["project"] == "PrompTopic - An AI Prompting Tool | GitHub"

    assert all(project["metadata"] == [] for project in result)
    assert all(project["description"] for project in result)