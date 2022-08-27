import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'my_project'
    API_PREFIX: str = '/api'
    SCHEMA_URL: str = '/api/schema.json'

    STATIC_ROOT: str = '/var/www/static'
    STATIC_URL: str = '/static/'
    MEDIA_ROOT: str = '/var/www/media'
    MEDIA_URL: str = '/media/'

    class Config:
        env_file = os.environ['FASTAPI_DOTENV']
