from typing import AsyncIterable

from .session import GlobalSession, SessionMeta, Session as Session_

# _local_db: ContextVar[Session_] = ContextVar('local_db')


class DbDependency:
    def __init__(self, Session: SessionMeta | None = None):
        self.Session = Session

    async def __call__(self) -> AsyncIterable[Session_]:
        Session = self.Session or GlobalSession
        async with Session() as db:
            try:
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise
            finally:
                await db.close()

get_db = DbDependency()
