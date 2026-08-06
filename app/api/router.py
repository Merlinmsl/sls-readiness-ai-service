from fastapi import APIRouter

from app.api.routes import health, profile


root_router = APIRouter()
root_router.include_router(health.router)


api_v1_router = APIRouter()
api_v1_router.include_router(profile.router)