import logging
import time
from typing import Optional

import httpx
from fastapi import Cookie, HTTPException
from jose import jwt

from .config import config
from .models.auth import User

GH_API_URL = "https://github.com/login/oauth/access_token"
GH_USER_API = "https://api.github.com/user"
GH_REPO_PERMISSION_API = "https://api.github.com/repos/{owner}/{repo}"
JWT_EXPIRY_SECONDS = 43200  # 12 hours


async def make_jwt(code: str):
    """Make a JWT token after validating the OAuth2 code with GitHub.
    Args:
        code: The OAuth2 code received from GitHub after user authorization.
    Returns:
        A JWT token as a string.
    Raises:
        HTTPException: If the OAuth token retrieval or user information fetch fails.
    """
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GH_API_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": config.GITHUB_CLIENT_ID,
                "client_secret": config.GITHUB_CLIENT_SECRET,
                "code": code,
            },
        )

        token_json = token_res.json()
        token = token_json.get("access_token")
        if "error" in token_json:
            error_msg = f"GitHub OAuth error: {token_json.get('error')}"
            if "error_description" in token_json:
                error_msg += f" - {token_json.get('error_description')}"
            raise HTTPException(status_code=400, detail=error_msg)
        if not token:
            raise HTTPException(
                status_code=400, detail="Failed OAuth token: missing access_token"
            )

        try:
            user_res = await client.get(
                GH_USER_API, headers={"Authorization": f"token {token}"}
            )
            github_user = user_res.json()
            repo_res = await client.get(
                GH_REPO_PERMISSION_API.format(
                    owner=config.GITHUB_REPO_OWNER, repo=config.GITHUB_REPO_NAME
                ),
                headers={"Authorization": f"token {token}"},
            )
            repo_data = repo_res.json()
            perm_data = repo_data.get("permissions", {})
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"GitHub user / repo permission request failed: {str(e)}",
            )

    # Make a JWT
    current_time = int(time.time())
    jwt_token = jwt.encode(
        {
            "iss": "mmsdb",
            "id": github_user["id"],
            "sub": github_user["login"],
            "full_name": github_user.get("name"),
            "email": github_user.get("email"),
            "role": "admin" if perm_data.get("push", False) else "contributor",
            "iat": current_time,
            "exp": current_time + JWT_EXPIRY_SECONDS,
        },
        config.JWT_SECRET,
        algorithm="HS256",
    )
    return jwt_token


def get_user(token: Optional[str] = Cookie(None, alias="token")) -> User:
    """Get, decode and validate a JWT token and make a user.

    Args:
        token: The JWT token to validate.

    Returns:
        The user associated with the JWT token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    if not token:
        raise HTTPException(status_code=401, detail="missing_token")
    try:
        # decoding also performs validation of issuer and exp claims
        decoded = jwt.decode(
            token, config.JWT_SECRET, issuer="mmsdb", algorithms=["HS256"]
        )
        return User(
            username=decoded.get("sub"),
            email=decoded.get("email", None),
            full_name=decoded.get("full_name", decoded.get("sub")),
            role=decoded.get("role", "contributor"),
        )
    except Exception as e:
        logging.exception("Failed to decode JWT token", e)
        raise HTTPException(status_code=401, detail="invalid_token")


def get_admin_user(token: Optional[str] = Cookie(None, alias="token")) -> User:
    """Get user from token and make sure role is admin.

    Args:
        token: The JWT token to validate.

    Returns:
        The user associated with the JWT token.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    user = get_user(token)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="insufficient_permissions")
    return user
