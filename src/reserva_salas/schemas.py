from pydantic import BaseModel


class RequestData(BaseModel):
    email: str
    senha: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class ChangePassword(BaseModel):
    email: str
    senha_antiga: str
    senha_nova: str
