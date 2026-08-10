from ..configs.header_configs import SECTION_HEADERS,PROJECT_HEADERS
from ..configs.project_configs import PROJECT_METADATA_KEYWORDS
from ..utils.text_utils import contains_keywords,_is_project_title,_is_project_metadata

def _extract_projects(text:str)->list[list[str]]|None:
    projects = []
    curr_project = []
    lines = text.split("\n")
    inside_projects = False

    for line in lines:
        line = line.strip()
        if not inside_projects:
            if contains_keywords(line,PROJECT_HEADERS):
                inside_projects = True
            continue
        if contains_keywords(line,SECTION_HEADERS):
            break
        if line:
            if line.startswith(("•", "-", "*")):
                    curr_project.append(line)
            elif _is_project_metadata(line,PROJECT_METADATA_KEYWORDS):
                curr_project.append(line)
            elif _is_project_title(line):
                    if curr_project:
                       projects.append(curr_project)
                    curr_project = [line]
            elif curr_project:
                curr_project[-1]+= " "+ line
    if curr_project:
       projects.append(curr_project)
    return projects if projects else None

def _parse_projects(blocks:list[list[str]])->list[dict]|None:
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
            elif _is_project_metadata(line,PROJECT_METADATA_KEYWORDS):
                project['metadata'].append(line)
            elif _is_project_title(line):
                project['project'] = line  
            else:
                project['description'].append(line)
            

        project_blocks.append(project)
    return project_blocks if project_blocks else None

def process_projects(text:str)->list[dict]|None:
    blocks = _extract_projects(text)

    if not blocks:
        return None
    return _parse_projects(blocks)