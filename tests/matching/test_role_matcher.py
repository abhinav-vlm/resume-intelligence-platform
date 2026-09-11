from src.configs.matching_roles import CANONICAL_ROLES
from src.matching.role_matcher import match_roles


def test_exact_role_match():
    result = match_roles(
        ["Machine Learning Engineer"],
        "Machine Learning Engineer"
    )

    assert result["candidate_roles"] == [
        "Machine Learning Engineer"
    ]
    assert result["target_role"] == "Machine Learning Engineer"
    assert result["canonical_candidate_roles"] == [
        CANONICAL_ROLES["machine learning engineer"]
    ]
    assert result["canonical_target_role"] == (
        CANONICAL_ROLES["machine learning engineer"]
    )
    assert result["status"] == "match"


def test_role_alias_match():
    result = match_roles(
        ["ML Engineer"],
        "Machine Learning Engineer"
    )

    assert result["canonical_candidate_roles"] == [
        "machine learning engineer"
    ]
    assert result["canonical_target_role"] == (
        "machine learning engineer"
    )
    assert result["status"] == "match"


def test_seniority_does_not_affect_role_match():
    result = match_roles(
        ["Senior ML Engineer"],
        "ML Engineer"
    )

    assert result["status"] == "match"


def test_junior_role_matches_same_role_family():
    result = match_roles(
        ["Junior ML Engineer"],
        "Machine Learning Engineer"
    )

    assert result["status"] == "match"


def test_different_known_roles_are_mismatch():
    result = match_roles(
        ["Data Analyst"],
        "ML Engineer"
    )

    assert result["status"] == "mismatch"


def test_multiple_roles_with_matching_role():
    result = match_roles(
        [
            "Data Analyst",
            "Software Engineer",
            "ML Engineer",
        ],
        "Machine Learning Engineer"
    )

    assert result["status"] == "match"
    assert result["canonical_candidate_roles"] == [
        "data analyst",
        "software engineer",
        "machine learning engineer",
    ]


def test_multiple_known_roles_without_match():
    result = match_roles(
        [
            "Data Analyst",
            "Software Engineer",
        ],
        "ML Engineer"
    )

    assert result["status"] == "mismatch"


def test_unknown_candidate_role():
    result = match_roles(
        ["Python Developer"],
        "Backend Engineer"
    )

    assert result["canonical_candidate_roles"] == [None]
    assert result["status"] == "unknown"


def test_unknown_candidate_role_with_matching_role():
    result = match_roles(
        [
            "Python Developer",
            "ML Engineer",
        ],
        "Machine Learning Engineer"
    )

    assert result["canonical_candidate_roles"] == [
        None,
        "machine learning engineer",
    ]
    assert result["status"] == "match"


def test_empty_candidate_roles():
    result = match_roles(
        [],
        "ML Engineer"
    )

    assert result["canonical_candidate_roles"] == []
    assert result["canonical_target_role"] == (
        "machine learning engineer"
    )
    assert result["status"] == "unknown"


def test_missing_target_role():
    result = match_roles(
        ["ML Engineer"],
        None
    )

    assert result["canonical_target_role"] is None
    assert result["status"] == "unknown"


def test_unknown_target_role():
    result = match_roles(
        ["ML Engineer"],
        "Some Completely Unknown Role"
    )

    assert result["canonical_target_role"] is None
    assert result["status"] == "unknown"


def test_role_normalization():
    result = match_roles(
    ["  SENIOR   ML   ENGINEER  "],
    "machine learning engineer")
    assert result["status"] == "match"