"""Development mode authentication middleware for testing."""
from fastapi import Request
from app.core.config import settings
from app.repositories.user_repository import user_repository


async def dev_auth_middleware(request: Request, call_next):
    """
    Development mode authentication middleware.

    In development mode, this middleware injects a fake user into request.state
    to simulate authentication without requiring a valid JWT token.

    This is only active when settings.DEV_MODE is True.
    """
    if settings.DEV_MODE:
        # Inject fake user for development
        request.state.user = {
            "user_id": settings.DEV_USER_ID,
            "username": settings.DEV_USERNAME,
            "real_name": settings.DEV_REAL_NAME,
            "email": None,
            "phone": None,
            "department_id": None,
            "department_name": None,
            "position": None
        }

    # Continue processing the request
    response = await call_next(request)
    return response
