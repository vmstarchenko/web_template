from typing import AsyncIterable

from .session import SessionMeta, Session


class DbDependency:
    def __init__(self):
        self.engine = None

    async def __call__(self) -> AsyncIterable[Session]:
        async with Session(self.engine) as db:
            try:
                yield db
                await db.commit()
            except:
                await db.rollback()
                raise
            finally:
                await db.close()

    def init(self, engine):
        self.engine = engine

get_db = DbDependency()
