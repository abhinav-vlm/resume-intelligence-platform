from fastapi import File,UploadFile
from ..parsers.pdf_parser import extract_text
from ..parsers.text_parser import clean_text
from ..parsers.email_parser import extract_email
from ..parsers.phone_parser import extract_phone
from ..parsers.name_parser import extract_name
from ..parsers.skills_parser import extract_skills
from ..parsers.education_parser import process_education
from ..parsers.experience_parser import process_experience
from ..parsers.project_parser import process_projects

async def process_resume(file:UploadFile):
    if file.content_type != "application/pdf":
        return{
             "error":"Only PDF files allowed"
        }
        
    content = await file.read()
    
    text = extract_text(content)
 
    cleaned_text = clean_text(text)

    email = extract_email(cleaned_text)

    phone = extract_phone(cleaned_text)

    name = extract_name(cleaned_text)

    skills = extract_skills(cleaned_text)

    education = process_education(cleaned_text)

    experience = process_experience(cleaned_text)

    projects = process_projects(cleaned_text)

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