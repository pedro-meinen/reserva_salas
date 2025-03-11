from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario: str
    email: str = Field(unique=True, index=True)
    senha: str


class Token(SQLModel, table=True):
    id_usuario: int
    access_token: str = Field(primary_key=True)
    refresh_token: str
    status: bool
    data_criacao: datetime = Field(default=datetime.now)


class Sala(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    capacidade: int = Field(gt=0)


class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reservado_por: Optional[int] = Field(default=None, foreign_key="usuario.id")
    sala_reservada: int = Field(foreign_key="sala.id", nullable=False)
    data_inicial: datetime
    data_final: datetime
    descricao: str
    tipo_evento: str
    quantidade_pessoas: int
    items: str = Field(nullable=True)
