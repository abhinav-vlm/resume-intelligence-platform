from ..configs.header_configs import SECTION_HEADERS, PROJECT_HEADERS
from ..configs.project_configs import PROJECT_METADATA_KEYWORDS
from ..utils.text_utils import (
    contains_keywords,
    _is_likely_skill_list,
    _is_project_title,
    _is_project_metadata,
)


def _next_meaningful_text(
    text_blocks: list[dict],
    index: int,
) -> str | None:
    for next_index in range(index + 1, len(text_blocks)):
        text = text_blocks[next_index]["text"].strip()

        if text:
            return text

    return None


def _extract_projects(
    text_blocks: list[dict],
) -> list[list[dict]] | None:

    projects = []
    curr_project = []

    inside_projects = False
    previous_page = None

    for i, line in enumerate(text_blocks):

        text = line["text"].strip()
        current_page = line["page"]

        # --------------------------------------------------------
        # Wait until PROJECTS section begins
        # --------------------------------------------------------
        if not inside_projects:

            if contains_keywords(text, PROJECT_HEADERS):
                inside_projects = True

            previous_page = current_page
            continue

        # --------------------------------------------------------
        # Stop when the next resume section begins
        # --------------------------------------------------------
        if contains_keywords(text, SECTION_HEADERS):
            break

        # --------------------------------------------------------
        # Ignore blank lines
        # --------------------------------------------------------
        if not text:
            previous_page = current_page
            continue

        page_changed = (
            previous_page is not None
            and current_page != previous_page
        )

        # --------------------------------------------------------
        # Bullet description
        # --------------------------------------------------------
        if text.startswith(("•", "-", "*", "‣", "●")):
            curr_project.append(line)

        # --------------------------------------------------------
        # Project metadata
        # --------------------------------------------------------
        elif _is_project_metadata(
            text,
            PROJECT_METADATA_KEYWORDS,
        ):
            curr_project.append(line)

        # --------------------------------------------------------
        # Wrapped description continuation
        #
        # Example:
        #
        #   • Built backend services using Python
        #   and FastAPI, PostgreSQL integration
        #
        # The second line contains a comma, so a generic
        # comma-based skill-list detector could incorrectly
        # classify it as:
        #
        #   FastAPI, PostgreSQL
        #
        # But because it starts with lowercase continuation text
        # and is on the same page, it belongs to the bullet above.
        # --------------------------------------------------------
        elif (
            curr_project
            and not page_changed
            and text[0].islower()
            and curr_project[-1]["text"].strip().startswith(
                ("•", "-", "*", "‣", "●")
            )
        ):
            curr_project[-1]["text"] += " " + text

        # --------------------------------------------------------
        # Skill-list noise
        #
        # Examples:
        #
        #   HTML, CSS
        #   React, Node.js
        #   Python, Docker
        #
        # These should neither become project titles nor be
        # appended to an existing project description.
        # --------------------------------------------------------
        elif _is_likely_skill_list(text):
            pass

        # --------------------------------------------------------
        # Possible project title
        # --------------------------------------------------------
        elif _is_project_title(text):

            next_text = _next_meaningful_text(
                text_blocks,
                i,
            )

            # ----------------------------------------------------
            # Page-boundary handling
            # ----------------------------------------------------
            if page_changed and curr_project:

                # If the first meaningful line on the new page
                # is immediately followed by a section boundary
                # or EOF, it is likely page-boundary noise rather
                # than a new project.
                if (
                    next_text is None
                    or contains_keywords(
                        next_text,
                        SECTION_HEADERS,
                    )
                ):
                    pass

                else:
                    projects.append(curr_project)
                    curr_project = [line]

            else:

                if curr_project:
                    projects.append(curr_project)

                curr_project = [line]

        # --------------------------------------------------------
        # Other continuation text
        # --------------------------------------------------------
        elif curr_project:

            # Same-page non-title text belongs to the current
            # project. Page-boundary text is deliberately ignored
            # unless it was confidently identified as a new title.
            if not page_changed:
                curr_project[-1]["text"] += " " + text

        previous_page = current_page

    # ------------------------------------------------------------
    # Flush final project
    # ------------------------------------------------------------
    if curr_project:
        projects.append(curr_project)

    return projects if projects else None


def _parse_projects(
    blocks: list[list[dict]],
    links: list[dict],
) -> list[dict] | None:

    project_blocks = []

    for block in blocks:

        project = {
            "project": None,
            "metadata": [],
            "description": [],
            "_bbox": None,
            "_page": None,
        }

        for line in block:

            text = line["text"].strip()

            # ----------------------------------------------------
            # Bullet description
            # ----------------------------------------------------
            if text.startswith(
                ("•", "-", "*", "‣", "●")
            ):
                project["description"].append(text)

            # ----------------------------------------------------
            # Project metadata
            # ----------------------------------------------------
            elif _is_project_metadata(
                text,
                PROJECT_METADATA_KEYWORDS,
            ):
                project["metadata"].append(text)

            # ----------------------------------------------------
            # Defensive skill-list filtering
            #
            # Normally _extract_projects() already removes these.
            # This protects the parser if such a line reaches this
            # layer through another code path.
            # ----------------------------------------------------
            elif _is_likely_skill_list(text):
                pass

            # ----------------------------------------------------
            # Project title
            # ----------------------------------------------------
            elif _is_project_title(text):

                project["_bbox"] = line["bbox"]
                project["_page"] = line["page"]
                project["project"] = text

            # ----------------------------------------------------
            # Other description content
            # ----------------------------------------------------
            else:
                project["description"].append(text)

        # --------------------------------------------------------
        # Associate links with the project title
        # --------------------------------------------------------
        if project["_bbox"] is not None:

            for link in links:

                if (
                    link["page"] == project["_page"]
                    and _boxes_overlap_y(
                        project["_bbox"],
                        link["bbox"],
                    )
                ):
                    project["metadata"].append(
                        {
                            "url": link["url"]
                        }
                    )

        project.pop("_bbox")
        project.pop("_page")

        project_blocks.append(project)

    return (
        project_blocks
        if project_blocks
        else None
    )


def _boxes_overlap_y(
    box1: tuple,
    box2: tuple,
) -> bool:

    y1_a, y2_a = box1[1], box1[3]
    y1_b, y2_b = box2[1], box2[3]

    return max(y1_a, y1_b) <= min(y2_a, y2_b)


def process_projects(
    text_blocks: list[dict],
    links: list[dict],
) -> list[dict] | None:

    blocks = _extract_projects(text_blocks)

    if not blocks:
        return None

    return _parse_projects(
        blocks,
        links,
    )