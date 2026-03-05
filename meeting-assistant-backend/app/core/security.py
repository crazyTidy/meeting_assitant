"""Security utility functions."""
from fastapi import Request
from typing import Optional, Dict, Any


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current user information from request.state.

    This should be called after auth_middleware has processed the request.

    Args:
        request: FastAPI Request object

    Returns:
        Dictionary containing user information (user_id, user_name, department_id, department_name)
        or None if user is not authenticated
    """
    return getattr(request.state, "user", None)


def require_auth(request: Request) -> Dict[str, Any]:
    """
    Get current user information and raise exception if not authenticated.

    This is a stricter version of get_current_user that always returns a user dict.

    Args:
        request: FastAPI Request object

    Returns:
        Dictionary containing user information

    Raises:
        HTTPException: If user is not authenticated
    """
    user = get_current_user(request)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user
