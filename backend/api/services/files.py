from functools import cache as functools_cache
from logging import getLogger
import os
import json
from pathlib import Path
import shutil
import subprocess
import mimetypes
import multiprocessing
from datetime import datetime

from fastapi import UploadFile

from api.config import config
from api.models.files import Contribution, FileInfo, UploadInfo


logger = getLogger("uvicorn.error")


ALLOWED_UPLOAD_SUFFIXES = [
    s.lower().strip() for s in config.UPLOAD_FILES_SUFFIX.split(",") if s
]


def cleanup_git_lock(repo_path: str):
    """Kill other git processes and remove .git/index.lock if exists."""
    try:
        subprocess.run(["pkill", "-f", "git"], check=False)
    except Exception:
        pass

    git_lock = Path(repo_path) / ".git" / "index.lock"
    if git_lock.exists():
        try:
            git_lock.unlink()
            logger.info(f"Removed git lock file: {git_lock}")
        except Exception as e:
            logger.warning(f"Failed to remove git lock file: {e}")


def cmd(command: str, working_directory: str | None = None) -> bytes:
    """Run a shell command with real-time logging."""

    logger.info(f"Running command: {command}")

    process = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_directory,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    stdout_lines = []
    stderr_lines = []

    while True:
        stdout_line = process.stdout.readline() if process.stdout else None
        stderr_line = process.stderr.readline() if process.stderr else None

        if stdout_line:
            logger.info(f"STDOUT: {stdout_line.rstrip()}")
            stdout_lines.append(stdout_line)

        if stderr_line:
            logger.error(f"STDERR: {stderr_line.rstrip()}")
            stderr_lines.append(stderr_line)

        if process.poll() is not None:
            break

    remaining_stdout, remaining_stderr = process.communicate()
    if remaining_stdout:
        for line in remaining_stdout.splitlines():
            if line.strip():
                logger.info(f"STDOUT: {line}")
                stdout_lines.append(line + "\n")

    if remaining_stderr:
        for line in remaining_stderr.splitlines():
            if line.strip():
                logger.error(f"STDERR: {line}")
                stderr_lines.append(line + "\n")

    return_code = process.returncode

    if return_code != 0:
        stderr_output = "".join(stderr_lines)
        raise Exception(f"Command failed: {command}\n{stderr_output}")

    stdout_output = "".join(stdout_lines)
    return stdout_output.strip().encode("utf-8")


def init_lfs_data():
    """Initialize LFS data by cloning the repository if not already done and checking out the specified git ref."""

    if not config.LFS_GIT_REF:
        logger.info("LFS_GIT_REF is not set. Using local data.")
        return

    lfs_server_url = config.LFS_SERVER_URL.replace(
        "https://", f"https://{config.LFS_USERNAME}:{config.LFS_PASSWORD}@"
    )
    credentials_line = f"{lfs_server_url}\n"
    git_credentials_path = Path.home() / ".git-credentials"
    with open(git_credentials_path, "a") as f:
        f.write(credentials_line)
    cmd("git config --global credential.helper store")

    if not os.path.exists(config.LFS_CLONED_REPO_PATH):
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
        cmd("git reset --hard", working_directory=config.LFS_CLONED_REPO_PATH)
        cmd("git clean -fdx", working_directory=config.LFS_CLONED_REPO_PATH)
        cmd(
            f"git checkout {config.LFS_GIT_REF}",
            working_directory=config.LFS_CLONED_REPO_PATH,
        )
        cmd("git pull", working_directory=config.LFS_CLONED_REPO_PATH)
        cmd("git lfs pull", working_directory=config.LFS_CLONED_REPO_PATH)

    logger.info("LFS data initialized.")


def _init_lfs_data_wrapper():
    try:
        init_lfs_data()
    except Exception as e:
        logger.error(f"Failed to initialize LFS data (subprocess): {e}")
        logger.warning("Continuing without up to date LFS data (subprocess).")
    finally:
        cleanup_git_lock(config.LFS_CLONED_REPO_PATH)


@functools_cache
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
    if not any(
        file.filename is not None and file.filename.lower().endswith(suffix)
        for file in files
        for suffix in valid_suffixes
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

    files_info = []
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
                    logger.debug(
                        f"Uploaded file: {unzipped_file_relative_path} ({size} bytes)"
                    )
                    files_info.append(
                        FileInfo(name=unzipped_file_relative_path.as_posix(), size=size)
                    )
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


multiprocessing.set_start_method("fork", force=True)
p = multiprocessing.Process(target=_init_lfs_data_wrapper)
p.start()
