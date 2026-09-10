from .api.resume_routes import router as resume_router
from .api.jd_routes import router as jd_router
from .api.matching_routes import router as match_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(resume_router)

app.include_router(jd_router)

app.include_router(match_router)