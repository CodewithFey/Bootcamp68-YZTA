from pydantic import BaseModel
from typing import Optional

# Token şeması
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Başarı mesajı şeması
class Message(BaseModel):
    message: str 