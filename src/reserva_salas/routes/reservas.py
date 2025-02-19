from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..bearer import JWTBearer, token_required
from ..database import get_session
from ..models import Reserva, Sala

router = APIRouter(prefix="/api/v1/reservas", tags=["Reservas"])


@router.get("/")
@token_required
async def obter_reservas(
    skip: int = 0,
    count: int = 10,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sequence[Reserva]:
    return session.exec(select(Reserva).offset(skip).limit(count)).all()


@router.get("/{id}")
@token_required
async def obter_reserva(
    id: int,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Reserva:
    reserva = session.exec(
        select(Reserva).where(Reserva.id == id).join(Sala)
    ).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrado")

    return reserva


@router.post("/")
@token_required
async def criar_reserva(
    reserva: Reserva,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Reserva:
    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.patch("/{id}")
@token_required
async def editar_reserva(
    id: int,
    reserva: Reserva,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Reserva:
    reserva_antiga = session.exec(
        select(Reserva).where(Reserva.id == id)
    ).first()

    if not reserva_antiga:
        raise HTTPException(404, "Reserva nao foi encontrado")

    reserva.id = reserva_antiga.id

    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.delete("/{id}")
@token_required
async def deletar_reserva(
    id: int,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    reserva = session.exec(select(Reserva).where(Reserva.id == id)).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrada")

    session.delete(reserva)
    session.commit()

    return {"mensagem": "Reserva deletada com sucesso"}
