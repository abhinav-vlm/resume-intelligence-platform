from fastapi import UploadFile
from src.parsers.jd_parser import parse_jd


async def process_jd(text: str | UploadFile):

    if isinstance(text, UploadFile):
        content = (await text.read()).decode("utf-8")
    else:
        content = text

    jd = parse_jd(content)

    return {
        "content": content,
        "jd": jd,
    }