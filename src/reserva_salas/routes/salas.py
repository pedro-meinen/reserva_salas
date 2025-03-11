from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Sala

router = APIRouter(prefix="/api/v1", tags=["Salas"])


@router.get("/sala")
async def obter_salas(
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[Sala]:
    return session.exec(select(Sala).offset(skip).limit(count)).all()


@router.get("/sala/{id_sala}")
async def obter_sala(
    id_sala: int, session: Annotated[Session, Depends(get_session)]
) -> Sala:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrado")

    return sala


@router.post("/sala")
async def criar_sala(
    sala: Sala, session: Annotated[Session, Depends(get_session)]
) -> Sala:
    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.patch("/sala/{id_sala}")
async def editar_sala(
    id_sala: int, sala: Sala, session: Annotated[Session, Depends(get_session)]
) -> Sala:
    sala_antiga = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala_antiga:
        raise HTTPException(404, "Sala nao foi encontrado")

    sala.id = sala_antiga.id

    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.delete("/sala/{id_sala}")
async def deletar_sala(
    id_sala: int, session: Annotated[Session, Depends(get_session)]
) -> Sala:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrada")

    session.delete(sala)
    session.commit()

    return sala
