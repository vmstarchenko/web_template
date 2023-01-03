import pytest
from dataclasses import dataclass
import re
import urllib.parse
from app.core import settings
import email
from aiosmtpd.controller import Controller


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


@pytest.fixture()
async def smtp_server():
    controller = Controller(SmtpServer(), hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
    try:
        controller.start()
        yield controller.handler
    finally:
        controller.stop()
