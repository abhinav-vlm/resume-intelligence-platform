from fastapi import File,UploadFile


async def process_resume(file:UploadFile):
    if file.content_type != "application/pdf":
        return{
             "error":"Only PDF files allowed"
        }
    return{
        "filename":file.filename,
        "content_type":file.content_type,
        "message":"Resume recieved successfully"
    }