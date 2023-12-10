from pydantic import BaseModel as BaseModel_, ConfigDict


class BaseModel(BaseModel_):
    model_config = ConfigDict(from_attributes=True)
