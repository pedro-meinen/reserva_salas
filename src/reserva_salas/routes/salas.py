from typing import Sequence
from fastapi import APIRouter

from ..models import Sala

router = APIRouter(prefix="/api/v1", tags=["Salas"])

@router.get("/sala")
async def obter_salas() -> Sequence[Sala]:
    ...

@router.get("/sala/{id}")
async def obter_sala(id: int) -> Sala:
    ...

@router.post("/sala")
async def criar_sala(sala: Sala) -> Sala:
    ...

@router.put("/sala/{id}")
async def editar_sala(id: int, sala: Sala) -> Sala:
    ...

@router.delete("/sala/{id}")
async def deletae_sala(id: int) -> Sala:
    ...