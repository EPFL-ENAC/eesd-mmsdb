from functools import cache as functools_cache
from logging import getLogger
import os
from pathlib import Path
import subprocess
import mimetypes
import multiprocessing

from api.config import config


logger = getLogger("uvicorn.error")


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


multiprocessing.set_start_method("fork", force=True)
p = multiprocessing.Process(target=_init_lfs_data_wrapper)
p.start()
