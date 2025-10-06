"""
Handle local file operations
"""

from pathlib import Path

from api.models.files import StonesResponse, extract_stone_number
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fastapi_cache.decorator import cache

from api.config import config
from api.services.files import get_local_file_content, list_local_files


router = APIRouter()


@router.get(
    "/get/{file_path:path}",
    status_code=200,
    description="Download any assets from local LFS repository",
)
# FastAPI in-memory cache does not support binary responses
async def get_file(
    file_path: str,
):
    base_path = Path(config.LFS_CLONED_REPO_PATH) / "data"
    full_file_path = (base_path / file_path).resolve()

    try:
        full_file_path.relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403, detail="Access denied: Path outside allowed directory"
        )

    try:
        body, content_type = get_local_file_content(full_file_path)
        if body is not None:
            headers = {
                "Content-Disposition": f"attachment; filename={Path(file_path).name}"
            }
            return Response(content=body, media_type=content_type, headers=headers)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.get(
    "/list/{directory_path:path}",
    status_code=200,
    description="List files in a given directory path in local LFS repository",
)
@cache()
async def list_files(
    directory_path: str,
):
    try:
        base_path = Path(config.LFS_CLONED_REPO_PATH) / "data"
        full_directory_path = (base_path / directory_path).resolve()

        try:
            full_directory_path.relative_to(base_path.resolve())
        except ValueError:
            raise HTTPException(
                status_code=403, detail="Access denied: Path outside allowed directory"
            )

        files = list_local_files(full_directory_path)

        files = [
            Path(path).relative_to(full_directory_path).as_posix() for path in files
        ]

        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/wall-path/{wall_id}",
    status_code=200,
    description='Get the local path for a given wall ID, in the form "OC01"',
)
@cache()
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


@router.get(
    "/wall-path/{wall_id}/stones",
    status_code=200,
    description='Get all the stones files paths for a given wall ID, in the form { folder: "/path/to/folder", files: ["stone1.ply", "stone2.ply"] }',
)
@cache()
async def get_wall_stones_paths_by_wall_id(
    wall_id: str,
) -> StonesResponse | None:
    wall_path = await get_wall_path(wall_id)
    if not wall_path:
        return None

    stones_dir = f"{wall_path}/01_Stones_data"
    stone_files = (
        await list_files(f"downscaled/01_Microstructures_data/{stones_dir}")
    )["files"]
    stone_files = [Path(f).name for f in stone_files if f.endswith(".ply")]
    stone_files.sort(key=extract_stone_number)

    return StonesResponse(folder=stones_dir, files=stone_files)
