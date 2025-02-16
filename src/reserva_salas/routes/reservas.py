from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from ..models import Reserva, Sala
from ..database import get_session

router = APIRouter(prefix="/api/v1", tags=["Reservas"])


@router.get("/reserva")
async def obter_reservas(session: Session = Depends(get_session)) -> Sequence[tuple[Reserva, Sala]]:
    return session.exec(select(Reserva, Sala).join(Sala)).all()


@router.get("/reserva/{id}")
async def obter_reserva(id: int, session: Session = Depends(get_session)) -> tuple[Reserva, Sala]:
    reserva = session.exec(select(Reserva, Sala).where(Reserva.id == id).join(Sala)).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrado")

    return reserva


@router.post("/reserva")
async def criar_reserva(reserva: Reserva, session: Session = Depends(get_session)) -> Reserva:
    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.put("/reserva/{id}")
async def editar_reserva(id: int, reserva: Reserva, session: Session = Depends(get_session)) -> Reserva:
    reserva_antiga = session.exec(select(Reserva).where(Reserva.id == id)).first()

    if not reserva_antiga:
        raise HTTPException(404, "Reserva nao foi encontrado")

    reserva.id = reserva_antiga.id

    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.delete("/reserva/{id}")
async def deletar_reserva(id: int, session: Session = Depends(get_session)) -> Reserva:
    reserva = session.exec(select(Reserva).where(Reserva.id == id)).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrada")

    session.delete(reserva)
    session.commit()

    return reserva