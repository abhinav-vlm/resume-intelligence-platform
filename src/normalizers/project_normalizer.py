

def normalize_projects(project:list[dict])->list[dict]:
    normalized_projects = []

    for entry in project:
        normalize_entry = {
            'project':entry.get('project'),
            'metadata':_normalize_metadata(entry.get('metadata',[])),
            'description':entry.get('description')
        }

        normalized_projects.append(normalize_entry)
    return normalized_projects

def _normalize_metadata(metadata:list[dict])->list[dict]:
    normalized_metadata = []
    
    for entry in metadata:
        url = entry.get("url")

        if not url:
           continue
        if 'github.com' in url:
            metadata_type = "github"
        elif 'linkedin.com' in url:
            continue
        else:
            metadata_type = "website"
        normalized_metadata.append({
            "type":metadata_type,
            "url":url
        })
    return normalized_metadata