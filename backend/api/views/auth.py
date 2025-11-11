import time
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from jose import jwt
import httpx
from urllib.parse import urlencode
from ..config import config

router = APIRouter()

GH_API_URL = "https://github.com/login/oauth/access_token"
GH_USER_API = "https://api.github.com/user"
GH_REPO_PERMISSION_API = "https://api.github.com/repos/{owner}/{repo}"


@router.get("/login")
async def login():
    redirect_uri = f"{config.APP_URL if config.PATH_PREFIX else 'http://localhost:8000'}{config.PATH_PREFIX}/auth/callback"
    params = {
        "client_id": config.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,  # e.g. https://your.app/auth/callback
        "scope": "read:user read:repo ",
    }
    github_authorize_url = (
        f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    )
    # return in response body the URL to redirect
    return {"url": github_authorize_url}


@router.get("/callback")
async def callback(code: str, response: Response):
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

        token = token_res.json().get("access_token")
        if not token:
            raise HTTPException(status_code=400, detail="Failed OAuth token")

        user_res = await client.get(
            GH_USER_API, headers={"Authorization": f"token {token}"}
        )
        github_user = user_res.json()

        owner = "EPFL-ENAC"
        repo = "eesd-mmsdb"

        repo_res = await client.get(
            GH_REPO_PERMISSION_API.format(owner=owner, repo=repo),
            headers={"Authorization": f"token {token}"},
        )
        repo_data = repo_res.json()
        perm_data = repo_data.get("permissions", {})
        if perm_data.get("push") is not True:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Make a JWT
    current_time = int(time.time())
    jwt_token = jwt.encode(
        {
            "issuer": "mmsdb",
            "id": github_user["id"],
            "sub": github_user["login"],
            "full_name": github_user.get("name"),
            "email": github_user.get("email"),
            "role": "admin" if perm_data.get("push") else "contributor",
            "issued_at": current_time,
            "exp": current_time + 3600 * 12,  # 12 hours
        },
        config.JWT_SECRET,
        algorithm="HS256",
    )

    # Set httpOnly cookie
    response = RedirectResponse(url=config.APP_URL)
    response.set_cookie(
        key="token",
        value=jwt_token,
        httponly=True,
        secure=False if config.APP_URL.startswith("http://localhost") else True,
        samesite="lax",
    )

    return response


@router.get("/userinfo")
async def userinfo(request: Request):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        decoded = jwt.decode(token, config.JWT_SECRET)
        if decoded["issuer"] != "mmsdb":
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        current_time = int(time.time())
        if decoded["exp"] < current_time:
            raise HTTPException(status_code=401, detail="Token expired")
        return decoded
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("token")
    response = Response()
    if token:
        response.delete_cookie(key="token")
    return response
