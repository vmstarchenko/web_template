from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session as OrmSession
# from sqlalchemy.pool import StaticPool


Session = AsyncSession
SessionMeta = type[Session]

GlobalSession: SessionMeta = sessionmaker(  # type: ignore
    expire_on_commit=False,
    class_=AsyncSession,
    sync_session_class=OrmSession,
)


def configure(uri, Session: SessionMeta | None=None):  # pylint: disable=redefined-outer-name
    Session = Session or GlobalSession
    engine = create_async_engine(
        uri,
        # future=True,
        # pool_pre_ping=True,
        # poolclass=StaticPool,
        # connect_args={'check_same_thread': False},
    )
    Session.configure(bind=engine)  # type: ignore

    return {'Session': Session, 'engine': engine}
