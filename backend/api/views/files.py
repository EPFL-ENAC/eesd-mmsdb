"""
Handle / uploads
"""

from pathlib import Path

from fastapi import Query, APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from api.config import config
from api.services.s3 import s3_client


class FilePath(BaseModel):
    paths: list[str]


router = APIRouter()


def cached(func):
    """Simple in-memory cache decorator for async functions"""
    cache = {}

    async def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = await func(*args, **kwargs)
        return cache[key]

    return wrapper


@router.get(
    "/get/{file_path:path}",
    status_code=200,
    description="Download any assets from S3",
)
async def get_file(
    file_path: str,
    download: bool = Query(
        False, alias="d", description="Download file instead of inline display"
    ),
):
    full_file_path = Path(config.S3_PATH_PREFIX) / file_path
    (body, content_type) = await s3_client.get_file(str(full_file_path))
    if body:
        if download:
            # download file
            return Response(
                content=body,
                media_type=content_type,
                headers={
                    "Content-Disposition": "attachment; filename="
                    + Path(file_path).name
                },
            )
        else:
            # inline image
            return Response(content=body)
    else:
        raise HTTPException(status_code=404, detail="File not found")


@cached
@router.get(
    "/list/{directory_path:path}",
    status_code=200,
    description="List files in a given directory path on S3",
)
async def list_files(
    directory_path: str,
):
    try:
        full_directory_path = Path(config.S3_PATH_PREFIX) / directory_path
        files = await s3_client.list_files(str(full_directory_path))
        files = [
            Path(path).relative_to(full_directory_path).as_posix() for path in files
        ]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@cached
@router.get(
    "/wall-path/{wall_id}",
    status_code=200,
    description='Get the S3 path for a given wall ID, in the form "OC01"',
)
async def get_wall_path(
    wall_id: str,
) -> str | None:
    wall_paths = (await list_files("downscaled/01_Microstructures_data"))["files"]
    wall_paths = [p for p in wall_paths if "02_Wall_data" in p and wall_id in p]

    if not wall_paths:
        return None

    wall_path = wall_paths[0]
    wall_path = wall_path[: wall_path.index("/02_Wall_data")]
    return wall_path
