from typing import AsyncIterable, Any
import functools

from fastapi.testclient import TestClient as Client
import pytest
from sqlalchemy.orm import sessionmaker


from app import deps, models
from app.db import configure, Session, BaseModel, SessionMeta, create_engine
from app.core import settings
from app.main import app
from sqlmodel import SQLModel

import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session as OrmSession
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# @pytest.fixture()
# def db(session: Session, client: Client) -> AsyncIterable[Session]:
#     for db in app.dependency_overrides[deps.get_db]():
#         yield db


@pytest.fixture(name="client")
def client_fixture(db: Session):
    def get_session_override():
        return db

    app.dependency_overrides[deps.get_db] = get_session_override
    with Client(app) as client:
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


@pytest.fixture()
def user(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = models.User.crud.create(
        db, email='test@test.example', password='password', username='user', is_active=True,
    )
    # obj.headers = get_user_headers(client, 'username', 'password')
    yield obj
    # obj.delete()  # TODO


@pytest.fixture()
def superuser(client: Client, db: Session) -> AsyncIterable[models.User]:
    obj = models.User.crud.create(
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
    yield get_user_headers(client, 'user', 'password')


@pytest.fixture()
def superuser_headers(client: Client, superuser: models.User) -> AsyncIterable[dict[str, str]]:
    yield get_user_headers(client, 'superuser', 'password')



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
