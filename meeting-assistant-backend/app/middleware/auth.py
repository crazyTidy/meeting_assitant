"""JWT authentication middleware."""
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from app.core.config import settings


# Public paths that don't require authentication
PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/demo/tokens",
    "/api/v1/users/login",
    "/api/v1/users/config"
}

# Public path prefixes that don't require authentication
PUBLIC_PATH_PREFIXES = {
    "/api/v1/meetings",  # Allow all meeting endpoints for development
}


async def auth_middleware(request: Request, call_next):
    """
    JWT authentication middleware: Parse token and inject user info into request.state.

    Supports two ways to pass token:
    1. Header: Authorization: Bearer <token>
    2. URL Parameter: ?token=<token>
    """

    # Skip authentication for public paths
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    # Skip authentication for public path prefixes
    for prefix in PUBLIC_PATH_PREFIXES:
        if request.url.path.startswith(prefix):
            return await call_next(request)

    # Skip authentication for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)

    token = None

    # Try to get token from Authorization header first
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    # If not in header, try URL parameter
    if not token:
        token = request.query_params.get("token")
        token = request.query_params.get("Token")  # 也支持大写

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Missing token",
                "usage": "Pass token via either Header or URL parameter",
                "header": "Authorization: Bearer <token>",
                "url": "?token=<token>",
                "example": f"{request.url.scheme}://{request.url.netloc}{request.url.path}?token=your-token-here"
            }
        )

    try:
        # Verify JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user information from payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id"
            )

        # Build user info dict
        user_info = {
            "user_id": user_id,
            "username": payload.get("username"),
            "real_name": payload.get("real_name"),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "department_id": payload.get("department_id"),
            "department_name": payload.get("department_name"),
            "position": payload.get("position")
        }

        # Inject user information into request.state
        request.state.user = user_info

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

    return await call_next(request)
