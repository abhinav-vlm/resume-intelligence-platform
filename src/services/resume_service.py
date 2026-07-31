from fastapi import File,UploadFile
from ..services.pdf_parser import extract_text
from ..services.text_parser import clean_text
from ..services.email_parser import extract_email
from ..services.phone_parser import extract_phone
from ..services.name_parser import extract_name

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

    return{
        "filename":file.filename,
        'text':cleaned_text,
        "email":email,
        "phone":phone,
        "name":name,
        "content_type":file.content_type,
        "message":"Resume received successfully"
    }