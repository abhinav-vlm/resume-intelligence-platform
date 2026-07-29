from fastapi import APIRouter
from fastapi import File,UploadFile
from ..services.resume_service import process_resume

router = APIRouter()

@router.get("/")
def home():
    return {"message":"Resume Intelligence Platform API"}

@router.post("/upload")
async def upload_resume(file:UploadFile=File(...)):
    return await process_resume(file)