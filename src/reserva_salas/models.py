from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel  # type: ignore


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario: str = Field(max_length=50, nullable=False)
    email: str = Field(max_length=100, unique=True, nullable=False)
    senha: str = Field(max_length=100, nullable=False)


class Token(SQLModel, table=True):
    id_usuario: int
    access_token: str = Field(max_length=450, primary_key=True)
    refresh_token: str = Field(max_length=350, nullable=False)
    status: bool
    data_criacao: datetime = Field(default=datetime.now)


class Sala(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str = Field(max_length=50)
    capacidade: int = Field(gt=0)


class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reservado_por: str = Field(max_length=50)
    sala_reservada: int = Field(foreign_key="sala.id")
    data_inicial: datetime
    data_final: datetime
    descricao: str = Field(max_length=256)
    tipo_evento: str = Field(max_length=50)
    quantidade_pessoas: int
    items: str = Field(max_length=25, nullable=True)
