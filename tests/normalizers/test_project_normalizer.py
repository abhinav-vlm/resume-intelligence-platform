from src.normalizers.project_normalizer import (
    normalize_projects,
    _normalize_metadata,
)


def test_normalize_metadata():
    metadata = [
        {"url": "https://github.com/Blockmecoder/Bloger"},
        {"url": "https://bloger.example.com"},
    ]

    result = _normalize_metadata(metadata)

    assert result == [
        {
            "type": "github",
            "url": "https://github.com/Blockmecoder/Bloger",
        },
        {
            "type": "website",
            "url": "https://bloger.example.com",
        },
    ]

def test_normalize_metadata_github_only():
    metadata = [
        {"url": "https://github.com/Blockmecoder/Bloger"}
    ]

    result = _normalize_metadata(metadata)

    assert result == [
        {
            "type": "github",
            "url": "https://github.com/Blockmecoder/Bloger"
        }
    ]

def test_normalize_metadata_website_only():
    metadata = [
        {"url": "https://bloger.example.com"}
    ]

    result = _normalize_metadata(metadata)

    assert result == [
        {
            "type": "website",
            "url": "https://bloger.example.com"
        }
    ]

def test_normalize_metadata_ignores_linkedin():
    metadata = [
        {"url": "https://linkedin.com/in/example"}
    ]

    result = _normalize_metadata(metadata)

    assert result == []

def test_normalize_metadata_missing_url():
    metadata = [
        {},
        {"url": None},
        {"url": ""},
        {"url": "https://github.com/example"}
    ]

    result = _normalize_metadata(metadata)

    assert result == [
        {
            "type": "github",
            "url": "https://github.com/example"
        }
    ]

def test_normalize_metadata_empty():
    result = _normalize_metadata([])

    assert result == []

def test_normalize_projects():
    projects = [
        {
            "project": "Bloger",
            "metadata": [
                {
                    "url": "https://github.com/Blockmecoder/Bloger"
                }
            ],
            "description": [
                "• Built a full-stack blog application.",
                "• Added authentication."
            ]
        }
    ]

    result = normalize_projects(projects)

    assert result == [
        {
            "project": "Bloger",
            "metadata": [
                {
                    "type": "github",
                    "url": "https://github.com/Blockmecoder/Bloger"
                }
            ],
            "description": [
                "• Built a full-stack blog application.",
                "• Added authentication."
            ]
        }
    ]

def test_normalize_multiple_projects():
    projects = [
        {
            "project": "Bloger",
            "metadata": [
                {"url": "https://github.com/example/bloger"}
            ],
            "description": ["• Built a blog."]
        },
        {
            "project": "Weather Sphere",
            "metadata": [
                {"url": "https://weather.example.com"}
            ],
            "description": ["• Built a weather app."]
        }
    ]

    result = normalize_projects(projects)

    assert len(result) == 2

    assert result[0]["project"] == "Bloger"
    assert result[0]["metadata"] == [
        {
            "type": "github",
            "url": "https://github.com/example/bloger"
        }
    ]

    assert result[1]["project"] == "Weather Sphere"
    assert result[1]["metadata"] == [
        {
            "type": "website",
            "url": "https://weather.example.com"
        }
    ]

def test_normalize_project_without_metadata():
    projects = [
        {
            "project": "Project Alpha",
            "description": [
                "• Built an application."
            ]
        }
    ]

    result = normalize_projects(projects)

    assert result == [
        {
            "project": "Project Alpha",
            "metadata": [],
            "description": [
                "• Built an application."
            ]
        }
    ]