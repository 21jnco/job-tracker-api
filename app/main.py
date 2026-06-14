from fastapi import FastAPI

from app.models.user import User
from app.models.job_application import JobApplication
from app.models.note import Note

from app.api.routers.auth import router as auth_router
from app.api.routers.job_applications import router as job_application_router
from app.api.routers.users import router as user_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(job_application_router)
app.include_router(user_router)