from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from starlette.middleware import cors, Middleware

from app.core import settings


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
    opendapi_url=f"{settings.API_PREFIX}/schema.json",
    middleware=middleware,
)

# Use nginx or fastapi for static and media files
# app.mount(settings.STATIC_URL, StaticFiles(directory=settings.STATIC_ROOT), name='static')
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name='media')

applications.get_swagger_ui_html = lambda *args, **kwargs: get_swagger_ui_html(
    *args, **kwargs,
    swagger_js_url='/static/js/swagger-ui-bundle.js',
    swagger_css_url='/static/css/swagger-ui.css',
    swagger_favicon_url='/favicon.ico',
)
