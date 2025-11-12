from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None
    role: str
