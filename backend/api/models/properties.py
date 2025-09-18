from pydantic import BaseModel


class Column(BaseModel):
    name: str
    values: list[str]


Table = list[Column]
