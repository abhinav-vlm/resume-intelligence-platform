from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from ..services.matching_service import match_resume_to_jd

router = APIRouter()


@router.post("/match")
async def match_resume_jd(
    resume_file: UploadFile = File(...),
    jd_text: str | None = Form(None),
    jd_file: UploadFile | None = File(None)
):
    if jd_text and jd_file or (not jd_file and not jd_text):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one JD input"
        )

    elif jd_text:
        return await match_resume_to_jd(resume_file, jd_text)

    else:
        return await match_resume_to_jd(resume_file, jd_file)