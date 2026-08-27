from os import error
from fastapi import File, UploadFile, APIRouter, Form, HTTPException
from ..services.jd_service import process_jd

router = APIRouter()

@router.post("/upload_jd")
async def upload_text_jd(jd_text:str|None = Form(None) ,file:UploadFile|None = File(None)):
    if jd_text and file or (not jd_text and not file):
        raise HTTPException(
                        status_code=400,
                        detail="Provide exactly one JD input"
                       )
    elif jd_text:
       return await process_jd(jd_text)
    elif file:
       return await process_jd(file)