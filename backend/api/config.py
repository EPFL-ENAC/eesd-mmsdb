from pydantic_settings import BaseSettings
from functools import lru_cache


class Config(BaseSettings):
    PATH_PREFIX: str
    S3_ENDPOINT_PROTOCOL: str
    S3_ENDPOINT_HOSTNAME: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    S3_REGION: str
    S3_BUCKET: str
    S3_PATH_PREFIX: str


@lru_cache()
def get_config():
    return Config()


config = get_config()
