from fastapi import APIRouter

from app.api.routes import health, process, profile


root_router = APIRouter()
root_router.include_router(health.router)


api_v1_router = APIRouter()
api_v1_router.include_router(profile.router)
api_v1_router.include_router(process.router)