import fitz
from fastapi import HTTPException
from starlette.datastructures import UploadFile
from src.parsers.jd_parser import parse_jd
from ..parsers.pdf_parser import extract_text


async def process_jd(text: str | UploadFile):
    if isinstance(text, UploadFile):
        content = await text.read()  
        try:
           text = extract_text(content)
        except fitz.FileDataError:
           raise HTTPException(
                  status_code=400,
                  detail="Invalid PDF file")
        
    jd = parse_jd(text)

    return {
        "text": text,
        "jd": jd,
    }