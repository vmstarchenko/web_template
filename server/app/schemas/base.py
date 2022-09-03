from pydantic.main import BaseModel as BaseModel_


class BaseModel(BaseModel_):
    class Config:
        orm_model = True
