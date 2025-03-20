from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.auth import TokenPayload, auth
from src.database import get_session
from src.models import Reserva, Sala, Usuario
from src.schemas import Resposta, mensagem

router = APIRouter(prefix="/api/v1/reservas", tags=["Reservas"])


@router.get("/")
async def obter_reservas(
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[tuple[Reserva, Sala, str]]:
    return session.exec(
        select(Reserva, Sala, Usuario.email)
        .join(Sala)
        .join(Usuario)
        .offset(skip)
        .limit(count)
    ).all()


@router.get("/{id_reserva}")
async def obter_reserva(
    id_reserva: int,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> tuple[Reserva, Sala, str]:
    reserva = session.exec(
        select(Reserva, Sala, Usuario.email)
        .where(Reserva.id == id_reserva)
        .join(Sala)
        .join(Usuario)
    ).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrado")

    return reserva


@router.post("/")
async def criar_reserva(
    reserva: Reserva,
    dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Reserva:
    usuario = int(dependencies.sub)

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não possui autorização para realizar essa operação",
        )

    reserva.reservado_por = usuario

    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.patch("/{id_reserva}")
async def editar_reserva(
    id_reserva: int,
    reserva: Reserva,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Reserva:
    reserva_antiga = session.exec(
        select(Reserva).where(Reserva.id == id_reserva)
    ).first()

    if not reserva_antiga:
        raise HTTPException(404, "Reserva nao foi encontrado")

    reserva.id_reserva = reserva_antiga.id

    session.add(reserva)
    session.commit()
    session.refresh(reserva)

    return reserva


@router.delete("/{id_reserva}")
async def deletar_reserva(
    id_reserva: int,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Resposta:
    reserva = session.exec(
        select(Reserva).where(Reserva.id == id_reserva)
    ).first()

    if not reserva:
        raise HTTPException(404, "Reserva nao foi encontrada")

    session.delete(reserva)
    session.commit()

    return mensagem("reserva deletada com sucesso")
