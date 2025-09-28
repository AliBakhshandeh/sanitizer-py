from fastapi import APIRouter
from app.controllers import upload_controller

router = APIRouter()

router.include_router(upload_controller.router)