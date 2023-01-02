from .session import Session

from sqlmodel import SQLModel


class BaseModel(SQLModel):
    __abstract__ = True

    def __str__(self) -> str:
        return f'<{type(self).__name__}: id={self.id}>'

    def __repr__(self) -> str:
        return f'<{type(self).__name__} object at 0x{id(self):x}: id={self.id}>'

    def save(self, db: Session) -> None:
        db.flush()
        db.refresh(self)
