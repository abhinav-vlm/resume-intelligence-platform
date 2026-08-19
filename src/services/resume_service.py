from fastapi import UploadFile
from ..parsers.pdf_parser import extract_text,extract_text_blocks,extract_links
from ..normalizers.education_normalizer import normalize_education
from ..normalizers.experience_normalizer import normalize_experience
from ..normalizers.skill_normalizer import normalize_skills
from ..parsers.text_parser import clean_text
from ..parsers.email_parser import extract_email
from ..parsers.phone_parser import extract_phone
from ..parsers.name_parser import extract_name
from ..parsers.skills_parser import extract_skills
from ..parsers.education_parser import process_education
from ..parsers.experience_parser import process_experience
from ..parsers.project_parser import process_projects
from ..normalizers.project_normalizer import normalize_projects

async def process_resume(file:UploadFile):
    if file.content_type != "application/pdf":
        return{
             "error":"Only PDF files allowed"
        }
    
    content = await file.read()
    
    text = extract_text(content)

    text_blocks = extract_text_blocks(content)
    
    links = extract_links(content)

    cleaned_text = clean_text(text)

    email = extract_email(cleaned_text)

    phone = extract_phone(cleaned_text)

    name = extract_name(cleaned_text)

    skills = extract_skills(cleaned_text)
    education = process_education(cleaned_text)
    experience = process_experience(cleaned_text)
    projects = process_projects(text_blocks, links)

    if education:
       education = normalize_education(education)

    if experience:
       experience = normalize_experience(experience)

    if projects:
       projects = normalize_projects(projects)

    if skills:
       skills = normalize_skills(skills)
       
    return{
        "filename":file.filename,
        'text':cleaned_text,
        "email":email,
        "phone":phone,
        "name":name,
        'education':education,
        'experience':experience,
        'projects':projects,
        'skills':skills,
        "content_type":file.content_type,
        "message":"Resume received successfully"
    }