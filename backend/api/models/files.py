# regex to capture the number from filenames like "OM01_stone_21.ply"
import re
from typing import List
from pydantic import BaseModel

STONE_NUMBER_REGEX = re.compile(r"_stone_(\d+)\.ply$")


def extract_stone_number(filename: str) -> int:
    match = STONE_NUMBER_REGEX.search(filename)
    return int(match.group(1)) if match else -1  # fallback if unexpected format


class StonesResponse(BaseModel):
    folder: str
    files: List[str]


class FileInfo(BaseModel):
    name: str
    size: int


class UploadInfo(BaseModel):
    path: str
    date: str
    files: List[FileInfo]
    total_size: int
    state: str = "uploaded"
    contributor: str
    comments: str | None = None
