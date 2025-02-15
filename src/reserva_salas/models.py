from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field # type: ignore

class Sala(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    capacidade: int


class Reserva(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reservado_por: str
    sala_reservada: int = Field(foreign_key="sala.id")
    data_inicial: datetime
    data_final: datetime
    descricao: str
    tipo_evento: str
    quantidade_pessoas: str
    items: str