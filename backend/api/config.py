from functools import lru_cache

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PATH_PREFIX: str
    APP_URL: str = "https://mmsdb-dev.epfl.ch"
    API_KEYS: str = "changeme"

    LFS_USERNAME: str
    LFS_PASSWORD: str
    LFS_REPO_URL: str = "https://github.com/EPFL-ENAC/eesd-mmsdb.git"
    LFS_SERVER_URL: str
    LFS_GIT_REF: str
    LFS_CLONED_REPO_PATH: str

    UPLOAD_FILES_PATH: str = "/tmp/mmsdb_upload"
    UPLOAD_FILES_SUFFIX: str = ".ply,.obj,.stl"

    PROPERTIES_PATH: str = "original/04_StoneMasonryMicrostructureDatabase.csv"
    STONE_PROPERTIES_DIR_PATH: str = "original/03_Stones_geometric_properties"

    # Mail/SMTP
    SMTP_HOST: str = "mail.epfl.ch"
    SMTP_PORT: int = 25
    SMTP_EMAIL: str = "noreply+mmsdb@epfl.ch"
    SMTP_NAME: str = "MMSDB"
    SMTP_PASSWORD: str = ""
    SMTP_USERNAME: str = ""
    MAIL_SUBJECT_PREFIX: str = "[MMSDB]"
    MAIL_ADMINISTRATORS: str = ""


@lru_cache()
def get_config():
    return Config()


config = get_config()
