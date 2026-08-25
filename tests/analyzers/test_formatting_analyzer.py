from src.analyzers.formatting_analyzer import (
    _analyze_bullet_formatting,
    _analyze_section_headers,
    _check_section_header_consistency,
    analyze_formatting
)

def test_bullet_formatting_consistent():
    experience = [
        {
            "description": [
                "• Built REST API",
                "• Added authentication",
                "• Improved performance",
            ]
        }
    ]

    result = _analyze_bullet_formatting(experience)

    assert result == [
        {
            "index": 0,
            "issues": [],
        }
    ]

def test_bullet_formatting_inconsistent():
    experience = [
        {
            "description": [
                "• Built REST API",
                "- Added authentication",
                "• Improved performance",
            ]
        }
    ]

    result = _analyze_bullet_formatting(experience)

    assert result == [
        {
            "index": 0,
            "issues": ["inconsistent_bullets"],
        }
    ]

def test_bullet_formatting_missing_bullet():
    experience = [
        {
            "description": [
                "• Built REST API",
                "Added authentication",
                "• Improved performance",
            ]
        }
    ]

    result = _analyze_bullet_formatting(experience)

    assert result == [
        {
            "index": 0,
            "issues": ["inconsistent_bullets"],
        }
    ]

def test_section_headers_detection():
    text = """
    EDUCATION :
    EXPERIENCE :
    PROJECTS :
    """

    result = _analyze_section_headers(text)

    assert result == [
        {
            "header": "EDUCATION",
            "has_colon": True,
        },
        {
            "header": "EXPERIENCE",
            "has_colon": True,
        },
        {
            "header": "PROJECTS",
            "has_colon": True,
        },
    ]

def test_section_headers_inconsistent_formatting():
    text = """
    EDUCATION :
    EXPERIENCE
    PROJECTS :
    """

    headers = _analyze_section_headers(text)

    result = _check_section_header_consistency(headers)

    assert result == [
        {
            "header": "EXPERIENCE",
            "issue": "inconsistent_header_format",
        }
    ]

def test_section_headers_consistent_formatting():
    text = """
    EDUCATION :
    EXPERIENCE :
    PROJECTS :
    """

    headers = _analyze_section_headers(text)

    result = _check_section_header_consistency(headers)

    assert result == []

def test_section_headers_empty():
    headers = []

    result = _check_section_header_consistency(headers)

    assert result == []

def test_unknown_lines_are_ignored_as_headers():
    text = """
    Some random text
    EDUCATION :
    Software Engineer
    """

    result = _analyze_section_headers(text)

    assert result == [
        {
            "header": "EDUCATION",
            "has_colon": True,
        }
    ]

def test_analyze_formatting():
    resume = {
        "text": """
        EDUCATION :
        EXPERIENCE :
        PROJECTS :
        """,
        "experience": [
            {
                "description": [
                    "• Built API",
                    "• Added authentication",
                ]
            }
        ],
        "projects": [],
    }

    result = analyze_formatting(resume)

    assert result == {
        "bullets": [
            {
                "index": 0,
                "issues": [],
            }
        ],
        "section_headers": [],
    }

def test_analyze_formatting_with_issues():
    resume = {
        "text": """
        EDUCATION :
        EXPERIENCE
        PROJECTS :
        """,
        "experience": [
            {
                "description": [
                    "• Built API",
                    "- Added authentication",
                ]
            }
        ],
        "projects": [],
    }

    result = analyze_formatting(resume)

    assert result["bullets"][0]["issues"] == [
        "inconsistent_bullets"
    ]

    assert result["section_headers"] == [
        {
            "header": "EXPERIENCE",
            "issue": "inconsistent_header_format",
        }
    ]