from urllib.parse import urlencode

from api.auth import get_user
from api.models.auth import User
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from ..auth import JWT_EXPIRY_SECONDS, make_jwt
from ..config import config

router = APIRouter()


@router.get("/login")
async def login():
    """Redirects to the URL from which the user can initiate the GitHub OAuth2 login flow.

    Returns:
        A JSON response containing the URL to redirect the user to for GitHub authentication.
    """
    redirect_uri = f"{config.APP_URL if config.PATH_PREFIX else 'http://localhost:8000'}{config.PATH_PREFIX}/auth/callback"
    params = {
        "client_id": config.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,  # e.g. https://your.app/auth/callback
        "scope": "read:user read:repo",
    }
    github_authorize_url = (
        f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    )
    # return in response body the URL to redirect
    return {"url": github_authorize_url}


@router.get("/callback")
async def callback(code: str, response: Response):
    jwt_token = await make_jwt(code)

    # Set httpOnly cookie
    response = RedirectResponse(url=f"{config.APP_URL}/contribute")
    response.set_cookie(
        key="token",
        value=jwt_token,
        httponly=True,
        secure=True if config.APP_URL.startswith("https") else False,
        samesite="lax",
        max_age=JWT_EXPIRY_SECONDS,
    )
    return response


@router.get("/userinfo")
async def userinfo(user: User = Depends(get_user)):
    return user


@router.delete("/session")
async def delete_session(request: Request):
    token = request.cookies.get("token")
    response = Response()
    if token:
        response.delete_cookie(key="token")
    return response
