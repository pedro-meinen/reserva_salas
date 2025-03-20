from datetime import datetime

from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario: str
    email: str = Field(unique=True, index=True)
    senha: str


class Sala(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nome: str
    capacidade: int = Field(gt=0)


class Reserva(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    reservado_por: int | None = Field(default=None, foreign_key="usuario.id")
    sala_reservada: int = Field(foreign_key="sala.id", nullable=False)
    data_inicial: datetime
    data_final: datetime
    descricao: str
    tipo_evento: str
    quantidade_pessoas: int
    items: str = Field(nullable=True)
