"""
Handle local file operations
"""

from io import BytesIO
from pathlib import Path
from uuid import uuid4
import zipfile

from api.models.files import StonesResponse, extract_stone_number
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse
from fastapi_cache.decorator import cache
from fastapi.datastructures import UploadFile
from fastapi.param_functions import File

from api.config import config
from api.services.files import (
    get_local_file_content,
    list_local_files,
    upload_local_files,
    delete_local_upload_folder,
)
from api.models.files import UploadInfo

router = APIRouter()


ALLOWED_UPLOAD_SUFFIXES = [
    s.lower().strip() for s in config.UPLOAD_FILES_SUFFIX.split(",") if s
]


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


@router.post(
    "/upload",
    status_code=200,
    description="Upload a file to the server (for admin use only)",
    response_model=UploadInfo,
)
async def upload_file(
    files: list[UploadFile] = File(description="multiple file upload"),
    contributor: str = "",
    comments: str | None = None,
) -> UploadInfo:
    """Upload a file to the server in the temporary upload directory, for further processing.

    Args:
        files (list[UploadFile]): List of files to upload
        contributor (str | None): Name or email of the contributor
        comments (str | None): Additional comments (optional)

    Raises:
        ValueError: If no valid upload file suffixes are configured
        HTTPException: If the file extension is invalid
        HTTPException: If the file upload fails
        HTTPException: If the file path is invalid

    Returns:
        UploadInfo: Information about the uploaded files
    """
    if contributor.strip() == "":
        raise HTTPException(
            status_code=400, detail="Contributor name or email is required"
        )
    if not ALLOWED_UPLOAD_SUFFIXES:
        raise ValueError("No valid UPLOAD_FILES_SUFFIX configured")
    # Check if all files have valid extensions
    if not any(
        file.filename.lower().endswith(suffix)
        for file in files
        for suffix in ALLOWED_UPLOAD_SUFFIXES
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension. Allowed extensions: {', '.join(ALLOWED_UPLOAD_SUFFIXES)}",
        )

    try:
        # Upload to folder path based on uuid4
        folder = str(uuid4())
        info = upload_local_files(
            folder, files=files, contributor=contributor, comments=comments
        )
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.delete(
    "/upload/{folder}",
    status_code=200,
    description="Delete an upload folder from the temporary upload directory (for admin use only)",
)
async def delete_upload_folder(folder: str):
    """Delete an upload folder from the temporary upload directory.

    Args:
        folder (str): Folder name to delete
    Raises:
        HTTPException: If the folder does not exist or deletion fails

    Returns:
        dict: Success message
    """
    base_path = Path(config.UPLOAD_FILES_PATH)
    folder_path = (base_path / folder).resolve()

    try:
        folder_path.relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403, detail="Access denied: Path outside allowed directory"
        )

    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    try:
        delete_local_upload_folder(folder)
        return {"detail": "Folder deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting folder: {str(e)}")


@router.get(
    "/upload/{folder}",
    status_code=200,
    description="Download an upload folder as a zip file (for admin use only)",
)
async def download_upload_folder(folder: str):
    """Download an upload folder as a zip file.

    Args:
        folder (str): Folder name to download
    Raises:
        HTTPException: If the folder does not exist or download fails
    Returns:
        Response: Zip file response
    """
    base_path = Path(config.UPLOAD_FILES_PATH)
    folder_path = (base_path / folder).resolve()

    try:
        folder_path.relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403, detail="Access denied: Path outside allowed directory"
        )

    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=404, detail="Folder not found")

    # Create an in-memory bytes buffer
    zip_buffer = BytesIO()

    # Create a ZIP file in memory
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                # Write file into zip, maintaining relative path
                zip_file.write(file_path, arcname=file_path.relative_to(folder_path))

    # Move cursor back to start of buffer
    zip_buffer.seek(0)

    # Stream response
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={folder_path.name}.zip"},
    )
