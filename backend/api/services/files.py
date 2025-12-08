import json
import mimetypes
import os
import shutil
import subprocess
from datetime import datetime
from functools import cache
from logging import getLogger
from pathlib import Path

from api.config import config
from api.models.files import Contribution, FileInfo, UploadInfo
from fastapi import HTTPException, UploadFile

logger = getLogger("uvicorn.error")


ALLOWED_UPLOAD_SUFFIXES = [
    s.lower().strip() for s in config.UPLOAD_FILES_SUFFIX.split(",") if s
]


@cache
def get_local_file_lfs_id(file_path: Path) -> str | None:
    """Check if a local file is a Git LFS pointer file."""
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r") as f:
            first_line = f.readline().strip()
            if first_line != "version https://git-lfs.github.com/spec/v1":
                return None

            second_line = f.readline().strip()
            if not second_line.startswith("oid sha256:"):
                return None

            return second_line.split(":")[1]

    except Exception:
        return None


@cache
def get_lfs_url(oid: str) -> str:
    """Get the download URL for a Git LFS object ID."""
    if not config.LFS_USERNAME or not config.LFS_PASSWORD:
        raise HTTPException(
            status_code=401, detail="LFS credentials are not configured"
        )

    url = config.LFS_SERVER_URL.replace(
        "https://", f"https://{config.LFS_USERNAME}:{config.LFS_PASSWORD}@"
    )

    return f"{url}/object/{oid}"


@cache
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


def upload_local_files(
    relative_path: str,
    files: list[UploadFile],
    contribution: Contribution | None = None,
) -> UploadInfo:
    """Upload a file to the temporary upload directory, expand zip files if needed and ensure file suffixes are allowed."""
    if not ALLOWED_UPLOAD_SUFFIXES:
        raise ValueError("No valid UPLOAD_FILES_SUFFIX configured")
    # Check if all files have valid extensions
    valid_suffixes = ALLOWED_UPLOAD_SUFFIXES[:]
    valid_suffixes.append(".zip")
    if not all(
        any(file.filename.lower().endswith(suffix) for suffix in valid_suffixes)
        for file in files
    ):
        raise ValueError(
            f"Invalid file extension. Allowed extensions: {', '.join(valid_suffixes)}"
        )

    base_path = Path(config.UPLOAD_FILES_PATH)
    folder_path = (base_path / relative_path).resolve()

    try:
        folder_path.relative_to(base_path.resolve())
    except ValueError:
        raise ValueError("Access denied: Path outside allowed directory")

    folder_path.mkdir(parents=True, exist_ok=True)

    files_info: list[FileInfo] = []
    for file_obj in files:
        full_file_path = folder_path / file_obj.filename
        # Check it is not relative path
        if ".." in file_obj.filename or file_obj.filename.startswith("/"):
            raise ValueError("Invalid file name")
        with open(full_file_path, "wb") as f:
            f.write(file_obj.file.read())
            if file_obj.content_type == "application/zip":
                # If zip file, unzip it in the same directory and remove the zip file
                shutil.unpack_archive(full_file_path, folder_path)
                full_file_path.unlink()
                # get list of unzipped files
                unzipped_files = [p for p in folder_path.rglob("*") if p.is_file()]
                for unzipped_file in unzipped_files:
                    # check if the unzipped file has a valid suffix
                    if not any(
                        unzipped_file.name.lower().endswith(suffix)
                        for suffix in ALLOWED_UPLOAD_SUFFIXES
                    ):
                        # remove the unzipped file
                        unzipped_file.unlink()
                        continue
                    # read local file size
                    size = os.path.getsize(unzipped_file)
                    unzipped_file_relative_path = unzipped_file.relative_to(folder_path)
                    logger.info(
                        f"Uploaded file: {unzipped_file_relative_path} ({size} bytes)"
                    )
                    posix_path = unzipped_file_relative_path.as_posix()
                    # Check file info does not already exist (could happen if multiple files uploaded)
                    if any(f.name == posix_path for f in files_info):
                        logger.warning(
                            f"File info already exists for {unzipped_file_relative_path}, skipping."
                        )
                        continue
                    files_info.append(FileInfo(name=posix_path, size=size))
            else:
                # read local file size
                size = os.path.getsize(full_file_path)
                files_info.append(FileInfo(name=file_obj.filename, size=size))
    total_size = sum(file.size for file in files_info)

    info = UploadInfo(
        path=relative_path,
        date=datetime.now().isoformat(),
        total_size=total_size,
        files=files_info,
        contribution=contribution,
    )
    # dump info to json file in the same directory
    with open(folder_path / "info.json", "w") as f:
        f.write(info.model_dump_json(indent=2))
    return info


def delete_local_upload_folder(relative_path: str) -> None:
    """Delete a folder from the temporary upload directory."""
    base_path = Path(config.UPLOAD_FILES_PATH)
    folder_path = (base_path / relative_path).resolve()

    try:
        folder_path.relative_to(base_path.resolve())
    except ValueError:
        raise ValueError("Access denied: Path outside allowed directory")

    if not folder_path.exists():
        # Nothing to do, silently return
        return
    if not folder_path.is_dir():
        raise ValueError("Provided path is not a directory")

    # Check there is a info.json file in the folder
    info_file = folder_path / "info.json"
    if not info_file.exists():
        raise FileNotFoundError("Upload info file does not exist in folder")

    shutil.rmtree(folder_path)

    return


def update_local_upload_info_state(relative_path: str, state: str) -> None:
    """Update the state field in the info.json file in the specified upload folder."""
    base_path = Path(config.UPLOAD_FILES_PATH)
    folder_path = (base_path / relative_path).resolve()

    try:
        folder_path.relative_to(base_path.resolve())
    except ValueError:
        raise ValueError("Access denied: Path outside allowed directory")

    if not folder_path.exists() or not folder_path.is_dir():
        raise FileNotFoundError("Upload folder does not exist")

    info_file = folder_path / "info.json"
    if not info_file.exists():
        raise FileNotFoundError("Upload info file does not exist in folder")

    try:
        with open(info_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["state"] = state
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to update state in info file: {e}")

    return
