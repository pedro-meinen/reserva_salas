from pydantic import BaseModel


class Resposta(BaseModel):
    label: str
    payload: str | bytes


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


def mensagem(conteudo: str | bytes) -> Resposta:
    return Resposta(label="mensagem", payload=conteudo)
