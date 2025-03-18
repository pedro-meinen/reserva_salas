from collections.abc import Sequence
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..bearer import JWTBearer, token_required
from ..database import get_session
from ..models import Reserva, Sala
from ..schemas import Resposta, mensagem

router = APIRouter(prefix="/api/v1/salas", tags=["Salas"])


@router.get("/")
@token_required
async def obter_salas(
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[Sala]:
    return session.exec(select(Sala).offset(skip).limit(count)).all()


@router.get("/disponiveis")
@token_required
async def obter_salas_disponiveis(
    data_inicial: datetime,
    data_final: datetime,
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
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

    if not salas:
        return mensagem("Nenhuma sala disponível")

    return salas


@router.get("/{id_sala}")
@token_required
async def obter_sala(
    id_sala: int,
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrado")

    return sala


@router.post("/")
@token_required
async def criar_sala(
    sala: Sala,
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.patch("/{id_sala}")
@token_required
async def editar_sala(
    id_sala: int,
    sala: Sala,
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
) -> Sala:
    sala_antiga = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala_antiga:
        raise HTTPException(404, "Sala nao foi encontrado")

    sala.id = sala_antiga.id

    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.delete("/{id_sala}")
@token_required
async def deletar_sala(
    id_sala: int,
    _dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
) -> Resposta:
    sala = session.exec(select(Sala).where(Sala.id == id_sala)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrada")

    session.delete(sala)
    session.commit()

    return mensagem("Sala deletada com sucesso")
