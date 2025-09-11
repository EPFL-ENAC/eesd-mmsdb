from pydantic import BaseModel


class Property(BaseModel):
    name: str
    value: str
