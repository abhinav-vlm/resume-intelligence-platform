

def normalize_project(project:list[dict])->list[dict]:
    normlaized_project = []

    for entry in project:
        normalize_entry = {
            'project':entry.get('project'),
            'metadata':[
                {'type':'github',
                'value': None},
                {'type':'live',
                'value': None}
            ],
            'description':entry.get('description')
        }
