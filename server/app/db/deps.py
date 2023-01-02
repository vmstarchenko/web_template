from typing import AsyncIterable

from .session import SessionMeta, Session as Session_

# _local_db: ContextVar[Session_] = ContextVar('local_db')


class DbDependency:
    def __init__(self, Session: SessionMeta | None = None):
        self.Session = Session

    def __call__(self) -> AsyncIterable[Session_]:
        Session = self.Session
        with Session() as db:
            try:
                yield db
                db.commit()
            except:
                db.rollback()
                raise
            finally:
                db.close()

get_db = DbDependency()
