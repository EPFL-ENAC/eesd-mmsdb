from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    PATH_PREFIX: str
    LFS_USERNAME: str
    LFS_PASSWORD: str
    LFS_REPO_URL: str = "https://github.com/EPFL-ENAC/eesd-mmsdb.git"
    LFS_SERVER_URL: str
    LFS_GIT_REF: str
    LFS_CLONED_REPO_PATH: str

    UPLOAD_FILES_PATH: str = "/tmp/mmsdb_upload"
    UPLOAD_FILES_SUFFIX: str = ".ply,.obj,.stl,.zip"

    PROPERTIES_PATH: str = "original/04_StoneMasonryMicrostructureDatabase.csv"
    STONE_PROPERTIES_DIR_PATH: str = "original/03_Stones_geometric_properties"


@lru_cache()
def get_config():
    return Config()


config = get_config()
