"""API v1 router."""
from fastapi import APIRouter
from app.api.v1.endpoints import meetings, participants, users, demo

api_router = APIRouter()

api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["meetings"]
)

api_router.include_router(
    participants.router,
    prefix="/meetings",
    tags=["participants"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    demo.router,
    prefix="/demo",
    tags=["demo"]
)
