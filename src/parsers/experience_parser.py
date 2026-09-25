from ..configs.experience_configs import ROLE_KEYWORDS
from ..utils.text_utils import is_duration, contains_keywords


BULLET_PREFIXES = ("•", "-", "*", "‣", "●")


def _extract_experience(
    text: str,
) -> list[list[str]] | None:

    lines = text.split("\n")

    experience = []
    curr_experience = []

    duration_found = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        is_bullet = line.startswith(BULLET_PREFIXES)
        is_duration_line = (
            is_duration(line)
            and not is_bullet
        )

        is_role_line = (
            contains_keywords(line, ROLE_KEYWORDS)
            and not is_bullet
            and not is_duration_line
        )

        # --------------------------------------------------------
        # A new experience begins at the next role.
        #
        # Example:
        #
        # Software Engineer
        # ABC Technologies
        # Jan 2024 - Present
        #
        # Data Analyst          <-- new experience starts here
        # XYZ Corporation
        # Jan 2021 - Dec 2023
        # --------------------------------------------------------
        if (
            is_role_line
            and duration_found
            and curr_experience
        ):
            experience.append(curr_experience)
            curr_experience = [line]
            duration_found = False

        else:
            curr_experience.append(line)

        if is_duration_line:
            duration_found = True

    if curr_experience:
        experience.append(curr_experience)

    return experience if experience else None


def _parse_experience(
    experience_blocks: list[list[str]],
) -> list[dict] | None:

    parsed_experience = []

    for block in experience_blocks:

        experience = {
            "company": None,
            "duration": None,
            "role": None,
            "description": [],
        }

        description_started = False

        for i, line in enumerate(block):

            is_bullet = line.startswith(BULLET_PREFIXES)

            # ----------------------------------------------------
            # Duration
            # ----------------------------------------------------
            if (
                is_duration(line)
                and not is_bullet
            ):

                experience["duration"] = line

                if i > 0:
                    experience["company"] = block[i - 1]

                description_started = False

            # ----------------------------------------------------
            # Role
            # ----------------------------------------------------
            elif contains_keywords(
                line,
                ROLE_KEYWORDS,
            ):

                experience["role"] = line
                description_started = False

            # ----------------------------------------------------
            # Bullet description
            # ----------------------------------------------------
            elif is_bullet:

                experience["description"].append(line)
                description_started = True

            # ----------------------------------------------------
            # Wrapped description
            # ----------------------------------------------------
            elif description_started:

                experience["description"][-1] += " " + line

        parsed_experience.append(experience)

    return (
        parsed_experience
        if parsed_experience
        else None
    )


def process_experience(
    text: str,
) -> list[dict] | None:

    blocks = _extract_experience(text)

    if not blocks:
        return None

    return _parse_experience(blocks)