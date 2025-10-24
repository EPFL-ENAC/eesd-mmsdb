"""
Handle local file operations
"""

from io import BytesIO
import logging
from pathlib import Path
from uuid import uuid4
import zipfile
import json
import re
from urllib.parse import unquote

from api.models.files import StonesResponse, extract_stone_number
from fastapi import APIRouter, HTTPException, Form, Security, BackgroundTasks
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
    update_local_upload_info_state,
    cleanup_git_lock,
    init_lfs_data,
)
from api.services.mailer import Mailer
from api.models.files import UploadInfo, Contribution, UploadInfoState
from api.auth import get_api_key

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
                "Content-Disposition": content_disposition(f"{Path(file_path).name}")
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
    description="Upload some files to the server",
    response_model=UploadInfo,
)
async def upload_file(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(description="multiple file upload"),
    contribution: str | None = Form(
        None, description="JSON string containing contribution information"
    ),
) -> UploadInfo:
    """Upload a file to the server in the temporary upload directory, for further processing.

    Args:
        files (list[UploadFile]): List of files to upload
        contribution (str | None): JSON string containing contribution information

    Raises:
        ValueError: If no valid upload file suffixes are configured
        HTTPException: If the file extension is invalid
        HTTPException: If the file upload fails
        HTTPException: If the file path is invalid
        HTTPException: If the contribution JSON is invalid

    Returns:
        UploadInfo: Information about the uploaded files
    """
    # Parse contribution JSON if provided
    contribution_obj = None
    if contribution:
        try:
            contribution_data = json.loads(contribution)
            contribution_obj = Contribution(**contribution_data)
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid contribution JSON: {str(e)}"
            )

    if not contribution_obj or (
        not contribution_obj.name and not contribution_obj.email
    ):
        raise HTTPException(
            status_code=400, detail="Contributor name or email is required"
        )

    try:
        # Upload to folder path based on uuid4
        folder = str(uuid4())
        info = upload_local_files(folder, files=files, contribution=contribution_obj)

        background_tasks.add_task(send_data_uploaded_email, info)

        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.delete(
    "/upload/{folder}",
    status_code=200,
    description="Delete an upload folder from the temporary upload directory",
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
    "/upload/{folder}/_state",
    status_code=200,
    description="Get the state of an upload folder",
    response_model=UploadInfoState,
)
async def get_upload_folder_state(folder: str):
    """Get the state of an upload folder in the temporary upload directory."""
    info = await get_upload_folder_info(folder, None)
    return UploadInfoState(path=info.path, state=info.state)


@router.get(
    "/upload/{path:path}",
    status_code=200,
    description="Download an upload folder as a zip file or an upload file as a single file",
)
async def download_upload_file(path: str):
    """Download an upload folder as a zip file or an upload file as a single file.

    Args:
        path (str): Path of the file or folder to download
    Raises:
        HTTPException: If the file or folder does not exist or download fails
    Returns:
        Response: Zip file response or single file response
    """
    base_path = Path(config.UPLOAD_FILES_PATH)
    # URL decode path
    decoded_path = unquote(path)
    file_path = (base_path / decoded_path).resolve()

    try:
        file_path.relative_to(base_path.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403, detail="Access denied: Path outside allowed directory"
        )

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if file_path.is_file():
        body, content_type = get_local_file_content(file_path)
        if body is not None:
            headers = {
                "Access-Control-Expose-Headers": "Content-Disposition",
                "Content-Disposition": content_disposition(f"{file_path.name}"),
            }
            return Response(content=body, media_type=content_type, headers=headers)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        # Create an in-memory bytes buffer
        zip_buffer = BytesIO()
        # Create a ZIP file in memory
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for f_path in file_path.rglob("*"):
                if f_path.is_file():
                    # Write file into zip, maintaining relative path
                    zip_file.write(f_path, arcname=f_path.relative_to(file_path))
        # Move cursor back to start of buffer
        zip_buffer.seek(0)

        # Stream response
        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={
                "Access-Control-Expose-Headers": "Content-Disposition",
                "Content-Disposition": content_disposition(f"{file_path.name}.zip"),
            },
        )


@router.get(
    "/upload-info",
    status_code=200,
    description="Get information about an upload folder (for admin use only)",
    response_model=list[UploadInfo],
)
async def get_upload_folders_info(
    api_key: str = Security(get_api_key),
) -> list[UploadInfo]:
    """Get information about all upload folders.

    Returns:
        list[UploadInfo]: Information about the uploaded files
    """
    base_path = Path(config.UPLOAD_FILES_PATH)

    if not base_path.exists() or not base_path.is_dir():
        return []
    upload_folders = [f for f in base_path.iterdir() if f.is_dir()]
    infos = []
    for folder_path in upload_folders:
        info_file_path = folder_path / "info.json"
        if not info_file_path.exists() or not info_file_path.is_file():
            continue
        try:
            with info_file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                infos.append(UploadInfo(**data))
        except Exception:
            continue
    return infos


@router.get(
    "/upload-info/{folder}",
    status_code=200,
    description="Get information about an upload folder (for admin use only)",
    response_model=UploadInfo,
)
async def get_upload_folder_info(
    folder: str, api_key: str = Security(get_api_key)
) -> UploadInfo:
    """Get information about an upload folder.

    Args:
        folder (str): Folder name to get information about
    Raises:
        HTTPException: If the folder does not exist or reading info fails
    Returns:
        UploadInfo: Information about the uploaded files
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

    info_file_path = folder_path / "info.json"
    if not info_file_path.exists() or not info_file_path.is_file():
        raise HTTPException(status_code=404, detail="Info file not found in folder")

    try:
        with info_file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return UploadInfo(**data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading info file: {str(e)}"
        )


@router.delete(
    "/upload-info/{folder}",
    status_code=200,
    description="Delete an upload folder from the temporary upload directory (for admin use only)",
)
async def delete_upload_folder_info(folder: str, api_key: str = Security(get_api_key)):
    """Delete an upload folder from the temporary upload directory.

    Args:
        folder (str): Folder name to delete
    Raises:
        HTTPException: If the folder does not exist or deletion fails

    Returns:
        dict: Success message
    """
    # Note: for consistency with list and get, we keep the same endpoint
    return delete_upload_folder(folder)


@router.put(
    "/upload-info/{folder}/_state",
    status_code=200,
    description="Update the state of an upload folder (for admin use only)",
    response_model=UploadInfo,
)
async def update_upload_folder_state(
    folder: str, state: str, api_key: str = Security(get_api_key)
) -> UploadInfo:
    """Update the state of an upload folder in the temporary upload directory.

    Args:
        folder (str): Folder name to update
        state (str): New state value
    Raises:
        HTTPException: If the folder does not exist or update fails
    Returns:
        UploadInfo: Updated information about the uploaded files
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
        update_local_upload_info_state(folder, state)
        return await get_upload_folder_info(folder, api_key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating info file: {str(e)}"
        )


def content_disposition(filename: str) -> str:
    """Generate a Content-Disposition header value that supports UTF-8 filenames."""
    safe_ascii = filename.encode("ascii", "ignore").decode()
    if not safe_ascii:
        safe_ascii = "download"

    # Sanitize ASCII fallback
    safe_ascii = re.sub(r"[^A-Za-z0-9._-]", "_", safe_ascii)

    return f'attachment; filename="{safe_ascii}"'


async def send_data_uploaded_email(info: UploadInfo):
    """Send an email notification when data is uploaded."""
    try:
        mailer = Mailer()
        await mailer.send_data_uploaded_email(info)
    except Exception as e:
        # Log error but do not block upload
        logging.error(f"Failed to send upload notification email: {e}")


@router.post("/refresh-lfs")
async def refresh_lfs_data(
    api_key: str = Security(get_api_key),
) -> None:
    """Refresh the local LFS data by pulling the latest changes from the remote repository."""
    try:
        cleanup_git_lock(config.LFS_CLONED_REPO_PATH)
        init_lfs_data()
    except Exception as e:
        logging.error(f"Failed to refresh LFS data (subprocess): {e}")
    finally:
        cleanup_git_lock(config.LFS_CLONED_REPO_PATH)
