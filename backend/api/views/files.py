"""
Handle local file operations
"""

from functools import cache
from pathlib import Path
import os
import subprocess
import mimetypes
from logging import getLogger

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from api.config import config


class FilePath(BaseModel):
    paths: list[str]


router = APIRouter()
logger = getLogger("uvicorn.error")


def cmd(command: str, working_directory: str | None = None) -> bytes:
    """Run a shell command."""

    result = subprocess.run(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
    )

    if result.returncode != 0:
        raise Exception(
            f"Command failed: {command}\n{result.stderr.decode('utf-8', errors='replace')}"
        )

    return result.stdout.strip()


def init_lfs_data():
    """Initialize LFS data by cloning the repository if not already done and checking out the specified git ref."""

    if not config.LFS_GIT_REF:
        logger.info("LFS_GIT_REF is not set. Using local data.")
        return

    if not os.path.exists(config.LFS_CLONED_REPO_PATH):
        lfs_server_url = config.LFS_SERVER_URL.replace(
            "https://", f"https://{config.LFS_USERNAME}:{config.LFS_PASSWORD}@"
        )
        credentials_line = f"{lfs_server_url}\n"
        git_credentials_path = Path.home() / ".git-credentials"
        with open(git_credentials_path, "a") as f:
            f.write(credentials_line)
        cmd("git config --global credential.helper store")

        logger.info("Creating parent directories for LFS repository clone...")
        os.makedirs(config.LFS_CLONED_REPO_PATH, exist_ok=True)
        logger.info("Cloning LFS repository...")
        cmd(f"git clone {config.LFS_REPO_URL} {config.LFS_CLONED_REPO_PATH}")
        cmd(
            f"git checkout {config.LFS_GIT_REF}",
            working_directory=config.LFS_CLONED_REPO_PATH,
        )
        cmd("git lfs pull", working_directory=config.LFS_CLONED_REPO_PATH)

    else:
        logger.info(
            "LFS repository already cloned. Checking out the specified git ref and pulling..."
        )
        cmd(
            f"git checkout {config.LFS_GIT_REF}",
            working_directory=config.LFS_CLONED_REPO_PATH,
        )
        cmd("git lfs pull", working_directory=config.LFS_CLONED_REPO_PATH)

    logger.info("LFS data initialized.")


def get_local_file_content(file_path: Path) -> tuple[bytes | None, str | None]:
    """Read file content and determine MIME type."""
    if not file_path.exists():
        return None, None

    with open(file_path, "rb") as f:
        content = f.read()

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    return content, mime_type


@cache
def list_local_files(directory_path: Path) -> list[str]:
    """List all files in a directory recursively."""
    logger.info(f"Listing files in directory: {directory_path}")
    if not directory_path.exists() or not directory_path.is_dir():
        return []

    files = []
    for item in directory_path.rglob("*"):
        if item.is_file():
            files.append(str(item))

    return files


@router.get(
    "/get/{file_path:path}",
    status_code=200,
    description="Download any assets from local LFS repository",
)
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


init_lfs_data()
