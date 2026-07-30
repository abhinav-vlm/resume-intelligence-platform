from src.services.pdf_parser import extract_text
from fastapi import File,UploadFile


async def process_resume(file:UploadFile):
    if file.content_type != "application/pdf":
        return{
             "error":"Only PDF files allowed"
        }
        
    content = await file.read()
    
    text = extract_text(content)

    return{
        "filename":file.filename,
        'text':text,
        "content_type":file.content_type,
        "message":"Resume recieved successfully"
    }