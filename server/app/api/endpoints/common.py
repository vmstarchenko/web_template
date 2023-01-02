import urllib.parse

from fastapi import APIRouter, Request
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from starlette.responses import RedirectResponse, HTMLResponse

from app.core import settings

# https://fastapi.tiangolo.com/advanced/extending-openapi/#self-hosting-javascript-and-css-for-docs


router = APIRouter()

DOCS_URL = '/docs'
DOCS_OAUTH_REDIRECT_URL = '/docs/oauth2-redirect'
REDOC_URL = '/redoc'


@router.get('/')
def index() -> RedirectResponse:
    return RedirectResponse('/info/')


@router.get('/info/')
def info(request: Request) -> dict[str, str]:
    return {
        'info': 'Hello! This is api info page.',
        'docs_url': str(request.url.replace(path=DOCS_URL)),
        'redoc_url': str(request.url.replace(path=REDOC_URL)),
    }


@router.get(DOCS_URL, include_in_schema=False)
def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url=settings.SCHEMA_URL,
        title=f'{settings.PROJECT_NAME} - Swagger UI',
        oauth2_redirect_url=DOCS_OAUTH_REDIRECT_URL,
        swagger_js_url=urllib.parse.urljoin(settings.STATIC_URL, 'js/swagger-ui-bundle.js'),
        swagger_css_url=urllib.parse.urljoin(settings.STATIC_URL, 'css/swagger-ui.css'),
        swagger_favicon_url='/favicon.ico',
    )


@router.get(DOCS_OAUTH_REDIRECT_URL, include_in_schema=False)
def swagger_ui_redirect() -> HTMLResponse:
    return get_swagger_ui_oauth2_redirect_html()


@router.get(REDOC_URL, include_in_schema=False)
def redoc_html() -> HTMLResponse:
    return get_redoc_html(
        openapi_url=settings.SCHEMA_URL,
        title=f'{settings.PROJECT_NAME} - ReDoc',
        redoc_js_url=urllib.parse.urljoin(settings.STATIC_URL, 'js/redoc.standalone.js'),
        redoc_favicon_url='/favicon.ico',
        with_google_fonts=False,
    )
