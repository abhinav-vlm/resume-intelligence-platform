from ..configs.header_configs import SECTION_HEADERS, PROJECT_HEADERS
from ..configs.project_configs import PROJECT_METADATA_KEYWORDS
from ..utils.text_utils import (
    contains_keywords,
    _is_project_title,
    _is_project_metadata,
)


def _next_meaningful_text(text_blocks: list[dict], index: int) -> str | None:
    for next_index in range(index + 1, len(text_blocks)):
        text = text_blocks[next_index]["text"].strip()
        if text:
            return text
    return None


def _extract_projects(text_blocks: list[dict]) -> list[list[dict]] | None:
    projects = []
    curr_project = []

    inside_projects = False
    previous_page = None

    for i, line in enumerate(text_blocks):
        text = line["text"].strip()
        current_page = line["page"]

        if not inside_projects:
            if contains_keywords(text, PROJECT_HEADERS):
                inside_projects = True
            previous_page = current_page
            continue

        if contains_keywords(text, SECTION_HEADERS):
            break

        if not text:
            previous_page = current_page
            continue

        page_changed = (
            previous_page is not None
            and current_page != previous_page
        )

        if text.startswith(("•", "-", "*")):
            curr_project.append(line)

        elif _is_project_metadata(text, PROJECT_METADATA_KEYWORDS):
            curr_project.append(line)

        elif _is_project_title(text):
            next_text = _next_meaningful_text(text_blocks, i)

            if page_changed and curr_project:
                if (
                    next_text is None
                    or contains_keywords(next_text, SECTION_HEADERS)
                ):
                    pass
                else:
                    projects.append(curr_project)
                    curr_project = [line]
            else:
                if curr_project:
                    projects.append(curr_project)

                curr_project = [line]

        elif curr_project:
            if not page_changed:
                curr_project[-1]["text"] += " " + text

        previous_page = current_page

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

            if text.startswith(("•", "-", "*")):
                project["description"].append(text)

            elif _is_project_metadata(
                text,
                PROJECT_METADATA_KEYWORDS,
            ):
                project["metadata"].append(text)

            elif _is_project_title(text):
                project["_bbox"] = line["bbox"]
                project["_page"] = line["page"]
                project["project"] = text

            else:
                project["description"].append(text)

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
                        {"url": link["url"]}
                    )

        project.pop("_bbox")
        project.pop("_page")

        project_blocks.append(project)

    return project_blocks if project_blocks else None


def _boxes_overlap_y(box1: tuple, box2: tuple) -> bool:
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

    return _parse_projects(blocks, links)