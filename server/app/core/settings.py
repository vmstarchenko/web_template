import secrets

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'my_project ффффф'
    API_PREFIX: str = '/api'
    SCHEMA_URL: str = f'{API_PREFIX}/schema.json'
    TOKEN_URL: str = f'{API_PREFIX}/user/login/'

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7     # one week
    USERS_OPEN_REGISTRATION = True

    STATIC_ROOT: str = '/var/www/static'
    STATIC_URL: str = '/static/'
    MEDIA_ROOT: str = '/var/www/media'
    MEDIA_URL: str = '/media/'

    DATABASE_URL: str   # "sqlite+aiosqlite:///./test.db"
    ENV_TYPE: str
