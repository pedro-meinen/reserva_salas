from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from src.auth import TokenPayload, auth
from src.database import get_session
from src.models import Reserva, Sala
from src.schemas import Resposta, mensagem

router = APIRouter(prefix="/api/v1/salas", tags=["Salas"])


@router.get("/")
async def obter_salas(
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[Sala]:
    return session.exec(select(Sala).offset(skip).limit(count)).all()


@router.get("/disponiveis")
async def obter_salas_disponiveis(
    data_inicial: datetime,
    data_final: datetime,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Sequence[tuple[int, Sala]] | Resposta:
    salas = session.exec(
        select(Reserva.sala_reservada, Sala)
        .where(
            (
                data_inicial < Reserva.data_final
                and data_inicial >= Reserva.data_inicial
            )
            or (
                data_final <= Reserva.data_final
                and data_final > Reserva.data_inicial
            )
            or (
                data_final >= Reserva.data_final
                and data_inicial <= Reserva.data_inicial
            )
        )
        .join(Sala)
    ).all()

    if salas is None:
        return mensagem("Nenhuma sala disponível")

    return salas


@router.get("/{id_sala}")
async def obter_sala(
    id_sala: int,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if sala is None:
        raise HTTPException(404, "Sala nao foi encontrado")

    return sala


@router.post("/")
async def criar_sala(
    sala: Sala,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.patch("/{id_sala}")
async def editar_sala(
    id_sala: int,
    sala: Sala,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    sala_antiga = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if sala_antiga is None:
        raise HTTPException(404, "Sala nao foi encontrado")

    sala.id = sala_antiga.id

    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.delete("/{id_sala}")
async def deletar_sala(
    id_sala: int,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Resposta:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if sala is None:
        raise HTTPException(404, "Sala nao foi encontrada")

    session.delete(sala)
    session.commit()

    return mensagem("Sala deletada com sucesso")
