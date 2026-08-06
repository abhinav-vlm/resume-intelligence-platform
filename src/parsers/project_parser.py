from ..configs.header_configs import SECTION_HEADERS,PROJECT_HEADERS
from ..utils.text_utils import contains_keywords

def extract_projects(text:str)->list[list[str]]|None:
    projects = []
    curr_project = []
    lines = text.split("\n")
    inside_projects = False
    inside_description = False

    for line in lines:
        line = line.strip()
        if not inside_projects:
            if contains_keywords(line,PROJECT_HEADERS):
                inside_projects = True
            continue
        if contains_keywords(line,SECTION_HEADERS):
            break
        if line:
            if not inside_description:
                if line.startswith(("•", "-", "*")):
                    inside_description = True
            if inside_description:
                if not line.startswith(("•", "-", "*")):
                    if curr_project:
                       projects.append(curr_project)
                    curr_project = []
                    inside_description = False
            curr_project.append(line)
    if curr_project:
       projects.append(curr_project)

    return projects if projects else None

def parse_projects(blocks:list[list[str]])->list[dict]|None:
    project_blocks = []
    for block in blocks:
        project = {
            "project":None,
            "metadata":[],
            "description":[]
        }
        for line in block:
            if line.startswith(("•", "-", "*")):
                project['description'].append(line)
            if project['project'] is None:
                project['project'] = line                
            else:
                project['metadata'].append(line)

        project_blocks.append(project)
    return project_blocks if project_blocks else None

def process_projects(text:str)->list[dict]|None:
    blocks = extract_projects(text)

    if not blocks:
        return None
    return parse_projects(blocks)