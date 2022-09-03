from contextvars import ContextVar
from typing import AsyncIterable

from .session import GlobalSession, SessionMeta, Session as Session_

_local_db: ContextVar[Session_] = ContextVar('local_db')


class DbDependency:
    def __init__(self, Session: SessionMeta | None = None):
        self.Session = Session

    @staticmethod
    def from_context():
        return _local_db.get()

    async def __call__(self) -> AsyncIterable[Session_]:
        Session = self.Session or GlobalSession
        async with Session() as db:
            token = None
            try:
                token = _local_db.set(db)
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise
            finally:
                await db.close()
                if token is not None:
                    if token.old_value:
                        _local_db.set(token.old_value)
                    else:
                        _local_db.reset(token)

get_db = DbDependency()
