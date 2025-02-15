from typing import Sequence
from fastapi import APIRouter

from ..models import Reserva

router = APIRouter(prefix="/api/v1", tags=["Reservas"])

@router.get("/reserva")
async def obter_reservas() -> Sequence[Reserva]:
    ...

@router.get("/reserva/{id}")
async def obter_reserva(id: int) -> Reserva:
    ...

@router.post("/reserva")
async def criar_reserva(reserva: Reserva) -> Reserva:
    ...

@router.put("/reserva/{id}")
async def editar_reserva(id: int, reserva: Reserva) -> Reserva:
    ...

@router.delete("/reserva/{id}")
async def deletae_reserva(id: int) -> Reserva:
    ...