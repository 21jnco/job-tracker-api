from fastapi import FastAPI

from app.models.user import User
from app.models.job_application import JobApplication
from app.models.note import Note

from app.api.routers.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)