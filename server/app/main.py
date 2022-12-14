from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware import cors, Middleware

from app.db import configure
from app.core import settings
from app.api.urls import router


# TODO: add correct origins, methods and headers
middleware = [
    Middleware(
        cors.CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.SCHEMA_URL,
    middleware=middleware,
	docs_url=None, redoc_url=None,
)

app.include_router(router)

# Use nginx or fastapi for static and media files
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name='media')

@app.on_event('startup')
def startup_event() -> None:
    if settings.ENV_TYPE == 'test':
        return

    configure(settings.DATABASE_URL)
