from src.configs.matching_roles import CANONICAL_ROLES


def match_roles(
    candidate_roles: list[str],
    target_role: str | None
) -> dict:

    matched = {
        "candidate_roles": candidate_roles,
        "target_role": target_role,
        "canonical_candidate_roles": [],
        "canonical_target_role": None,
        "status": None
    }

    canonical_target_role = None

    if target_role and target_role.strip().lower() in CANONICAL_ROLES:
        canonical_target_role = CANONICAL_ROLES.get(
            target_role.strip().lower()
        )

    matched["canonical_target_role"] = canonical_target_role

    for role in candidate_roles:
        canonical_candidate_role = None

        if role and role.strip().lower() in CANONICAL_ROLES:
            canonical_candidate_role = CANONICAL_ROLES.get(
                role.strip().lower()
            )

        matched["canonical_candidate_roles"].append(
            canonical_candidate_role
        )

    if canonical_target_role is None:
        matched["status"] = "unknown"
        return matched

    if not candidate_roles:
        matched["status"] = "unknown"
        return matched

    if canonical_target_role in matched["canonical_candidate_roles"]:
        matched["status"] = "match"
    elif None in matched["canonical_candidate_roles"]:
        matched["status"] = "unknown"
    else:
        matched["status"] = "mismatch"

    return matched