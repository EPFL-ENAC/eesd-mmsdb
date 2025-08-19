from pydantic import BaseModel


class Property(BaseModel):
    name: str
    value: str


class PropertyEntry(BaseModel):
    properties: list[Property]
