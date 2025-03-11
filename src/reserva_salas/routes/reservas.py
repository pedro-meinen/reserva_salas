from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models import Reserva, Sala

router = APIRouter(prefix="/api/v1", tags=["Reservas"])


@router.get("/reserva")
async def obter_reservas(
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[Reserva]:
    return session.exec(select(Reserva).offset(skip).limit(count)).all()


@router.get("/reserva/{id_reserva}")
async def obter_reserva(
    id_reserva: int, session: Annotated[Session, Depends(get_session)]
) -> Reserva:
    reserva = session.exec(
        select(Reserva).where(Reserva.id == id_reserva).join(Sala)
    ).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrado")

    return reserva


@router.get("/reserva/usuario/{username}")
async def obter_reservas_por_usuario(
    username: str,
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[Reserva]:
    return session.exec(
        select(Reserva)
        .where(Reserva.reservado_por == username)
        .offset(skip)
        .limit(count)
    ).all()


@router.post("/reserva")
async def criar_reserva(
    reserva: Reserva, session: Annotated[Session, Depends(get_session)]
) -> Reserva:
    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.patch("/reserva/{id_reserva}")
async def editar_reserva(
    id_reserva: int,
    reserva: Reserva,
    session: Annotated[Session, Depends(get_session)],
) -> Reserva:
    reserva_antiga = session.exec(
        select(Reserva).where(Reserva.id == id_reserva)
    ).first()

    if not reserva_antiga:
        raise HTTPException(404, "Reserva nao foi encontrado")

    reserva.id = reserva_antiga.id

    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.delete("/reserva/{id_reserva}")
async def deletar_reserva(
    id_reserva: int, session: Annotated[Session, Depends(get_session)]
) -> Reserva:
    reserva = session.exec(
        select(Reserva).where(Reserva.id == id_reserva)
    ).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrada")

    session.delete(reserva)
    session.commit()

    return reserva
