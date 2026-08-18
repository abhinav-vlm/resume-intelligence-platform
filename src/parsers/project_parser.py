from ..configs.header_configs import SECTION_HEADERS,PROJECT_HEADERS
from ..configs.project_configs import PROJECT_METADATA_KEYWORDS
from ..utils.text_utils import (
    contains_keywords,
    _is_project_title,
    _is_project_metadata
    )

def _extract_projects(text_blocks: list[dict]) -> list[list[dict]] | None:
    projects = []
    curr_project = []

    inside_projects = False

    for line in text_blocks:
        text = line["text"].strip()
        if not inside_projects:
            if contains_keywords(text,PROJECT_HEADERS):
                inside_projects = True
            continue
        if contains_keywords(text,SECTION_HEADERS):
            break
        if text:
            if text.startswith(("•", "-", "*")):
                    curr_project.append(line)
            elif _is_project_metadata(text,PROJECT_METADATA_KEYWORDS):
                curr_project.append(line)
            elif _is_project_title(text):
                    if curr_project:
                       projects.append(curr_project)
                    curr_project = [line]
            elif curr_project:
                curr_project[-1]["text"] += " " + text
    if curr_project:
       projects.append(curr_project)
    return projects if projects else None

def _parse_projects(blocks: list[list[dict]],links: list[dict]) -> list[dict] | None:

    project_blocks = []
    for block in blocks:
        project = {
            "project": None,
            "metadata": [],
            "description": [],
            "_bbox": None,
            "_page": None
               }
        for line in block:  
            text = line["text"].strip()     
            if text.startswith(("•", "-", "*")): 
                project['description'].append(text)       
            elif _is_project_metadata(text,PROJECT_METADATA_KEYWORDS):
                project['metadata'].append(text)
            elif _is_project_title(text):
                project["_bbox"] = line["bbox"]
                project["_page"] = line["page"]
                project['project'] = text
            else:
                project['description'].append(text)
        if project["_bbox"] is not None:
           for link in links:
               if link["page"] == project["_page"] and _boxes_overlap_y(project["_bbox"],link["bbox"]):
                  project['metadata'].append({"url":link['url']})
        project.pop("_bbox")
        project.pop("_page")
        project_blocks.append(project)
    return project_blocks if project_blocks else None

def _boxes_overlap_y(box1, box2) -> bool:
    y1_a = box1[1]
    y2_a = box1[3]
    y1_b = box2[1]
    y2_b = box2[3]
    if max(y1_a, y1_b) <= min(y2_a, y2_b):
        return True
    return False


def process_projects(text_blocks: list[dict],links: list[dict]) -> list[dict] | None:
    blocks = _extract_projects(text_blocks)

    if not blocks:
        return None
    return _parse_projects(blocks, links)