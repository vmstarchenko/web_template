import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "my_project"
    API_PREFIX: str = '/api'

    STATIC_ROOT: str = '/var/www/static'
    STATIC_URL: str = '/static/'
    MEDIA_ROOT: str = '/var/www/media'
    MEDIA_URL: str = '/media/'

    class Config:
        case_sensitive = True
        env_file = os.environ['FASTAPI_DOTENV']
