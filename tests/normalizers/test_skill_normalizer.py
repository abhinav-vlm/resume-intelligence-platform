from src.normalizers.skill_normalizer import normalize_skills

def test_normalize_skills():
    skills = ["Python","ReactJS","react.js","React JS"]

    result = normalize_skills(skills)
    assert result == ["Python","React"]

def test_normalize_skill_aliases():
    skills = [
        "ReactJS",
        "nodejs",
        "Next JS",
        "express.js",
        "sklearn",
    ]

    result = normalize_skills(skills)

    assert result == [
        "React",
        "Node.js",
        "Next.js",
        "Express.js",
        "Scikit-learn",
    ]

def test_normalize_skill_whitespace():
    skills = [
        " Python ",
        "  ReactJS  ",
        "Node.js ",
    ]

    result = normalize_skills(skills)

    assert result == [
        "Python",
        "React",
        "Node.js",
    ]

def test_normalize_skill_case():
    skills = [
        "REACTJS",
        "ReAcT.Js",
        "NODEJS",
    ]

    result = normalize_skills(skills)

    assert result == [
        "React",
        "Node.js",
    ]

def test_normalize_skill_duplicates():
    skills = [
        "ReactJS",
        "React.js",
        "React JS",
        "React",
    ]

    result = normalize_skills(skills)

    assert result == ["React"]

def test_unknown_skill_is_preserved():
    skills = [
        "Python",
        "SomethingObscure",
    ]

    result = normalize_skills(skills)

    assert result == [
        "Python",
        "SomethingObscure",
    ]
