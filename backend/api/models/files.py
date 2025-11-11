# regex to capture the number from filenames like "OM01_stone_21.ply"
import re
from typing import List

from pydantic import BaseModel

STONE_NUMBER_REGEX = re.compile(r"_stone_(\d+)\.ply$")


def extract_stone_number(filename: str) -> int:
    match = STONE_NUMBER_REGEX.search(filename)
    # fallback if unexpected format
    return int(match.group(1)) if match else -1


class StonesResponse(BaseModel):
    folder: str
    files: List[str]


class FileInfo(BaseModel):
    name: str
    size: int


class Contribution(BaseModel):
    name: str
    email: str
    affiliation: str | None = None
    comments: str | None = None
    type: str | None = None  # Microstructure type: Real or Virtual
    method: str | None = None  # Photogrammetry, CT scan, Procedural, Other
    reference: str | None = None  # Reference to a publication or project


class UploadInfo(BaseModel):
    path: str
    date: str
    files: List[FileInfo]
    total_size: int
    state: str = "uploaded"
    contribution: Contribution | None = None


class UploadInfoState(BaseModel):
    path: str
    state: str = "uploaded"
