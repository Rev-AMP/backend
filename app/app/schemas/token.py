from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    expiry: int


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    type: Optional[str] = None
