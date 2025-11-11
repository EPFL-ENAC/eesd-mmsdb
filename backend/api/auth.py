import time
from typing import Optional
from fastapi import HTTPException, status, Security, Cookie
from fastapi.security import APIKeyHeader

from .config import config
from jose import jwt
from .models.auth import User

API_KEYS = config.API_KEYS.split(",")

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


def get_api_key(
    api_key_header: str = Security(api_key_header),
) -> str:
    """Retrieve and validate an API key from the query parameters or HTTP header.

    Args:
        api_key_header: The API key passed in the HTTP header.

    Returns:
        The validated API key.

    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


def get_user(token: Optional[str] = Cookie(None, alias="token")) -> User:
    """Get, decode and validate a JWT token.

    Args:
        token: The JWT token to validate.

    Returns:
        The decoded JWT payload.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        decoded = jwt.decode(token, config.JWT_SECRET)
        if decoded["exp"] < int(time.time()):
            raise HTTPException(status_code=401, detail="Token expired")
        if decoded["issuer"] != "mmsdb":
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        return User(
            username=decoded.get("sub"),
            full_name=decoded.get("full_name", None),
            role=decoded.get("role", "contributor"),
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_admin_user(token: Optional[str] = Cookie(None, alias="token")) -> User:
    """Get, decode and validate a JWT token, make sure role is admin.

    Args:
        token: The JWT token to validate.

    Returns:
        The decoded JWT payload.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    user = get_user(token)
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Role not authorized")
    return user
