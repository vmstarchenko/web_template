from typing import AsyncIterable, Any
import functools

from fastapi.testclient import TestClient as Client
# from httpx import AsyncClient as Client
import pytest
from sqlalchemy.orm import sessionmaker


from app import deps, models
from app.db import configure, Session, BaseModel, SessionMeta, create_async_engine
from app.core import settings
from app.main import app
from sqlmodel import SQLModel

import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="db")
async def db_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    meta = BaseModel.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)
 
    async with Session(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)

    '''
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with AsyncSession(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        h = (await session.exec(statement)).first()
        print(h)  # name='Spider-Boy' id=2 age=None secret_name='Pedro Parqueador'
    '''
# @pytest.fixture()
# def db(session: Session, client: Client) -> AsyncIterable[Session]:
#     for db in app.dependency_overrides[deps.get_db]():
#         yield db


# @pytest.fixture()
# async def client(db_initials: Any) -> AsyncIterable[Client]:
#     async with Client(app=app, base_url='http://testhost.example') as client:
#         app.dependency_overrides[deps.get_db] = deps.DbDependency(Session=db_initials['Session'])
#         yield client


@pytest.fixture(name="client")
async def client_fixture(db: Session):
    def get_session_override():
        return db

    try:
        app.dependency_overrides[deps.get_db] = get_session_override
        with Client(app) as client:
        # async with Client(app=app, base_url='http://testhost.example') as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
async def user(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(
        db,
        email='user@test.example',
        password='password', username='user',
        is_active=True, is_verified=True,
    )
    # obj.headers = get_user_headers(client, 'username', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
async def superuser(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = await models.User.crud.create(
        db,
        email='superuser@test.example', password='password', username='superuser',
        is_superuser=True,
        is_active=True
    )
    # obj.headers = get_user_headers(client, 'superuser', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
def user_headers(client: Client, user: models.User) -> AsyncIterable[dict[str, str]]:
    yield get_user_headers(client, 'user@test.example', 'password')


@pytest.fixture()
def superuser_headers(client: Client, superuser: models.User) -> AsyncIterable[dict[str, str]]:
    yield get_user_headers(client, 'superuser@test.example', 'password')



def get_user_headers(client: Client, username: str, password: str) -> dict[str, str]:
    resp = client.post(settings.TOKEN_URL, data={
        'username': username, 'password': password
    })
    res = resp.json()
    assert resp.status_code == 200, res
    token = res.get('access_token')
    assert token, res

    return {'Authorization': f'Bearer {token}'}


from dataclasses import dataclass
import re
import urllib.parse

@dataclass
class EMail:
    sender: str
    recievers: list[str]
    content: str

    @property
    def links(self):
        # return [urllib.parse.urlparse(url) for url in re.findall(r'https?://[\S<>]+', self.content)]
        return re.findall(r'https?://[\S<>]+', self.content)


class SmtpServer:
    def __init__(self):
        self.mails = []

    async def handle_DATA(self, server, session, envelope):
        email = EMail(
            sender=envelope.mail_from,
            recievers=envelope.rcpt_tos,
            content=self.get_content(envelope.content),
        )
        self.mails.append(email)
        return '250 OK'

    @staticmethod
    def get_content(content):
        b = email.message_from_string(content.decode('utf-8'))
        body = []
        if b.is_multipart():
            for part in b.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype in ['text/plain', 'text/html'] and 'attachment' not in cdispo:
                    body.append(part.get_payload(decode=True))
        else:
            body.append(b.get_payload(decode=True))
        return b'\n'.join(body).decode('utf-8')

import email
from aiosmtpd.controller import Controller

@pytest.fixture()
async def smtp_server():
    controller = Controller(SmtpServer(), hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
    try:
        controller.start()
        yield controller.handler
    finally:
        controller.stop()
