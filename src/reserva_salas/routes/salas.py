from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..bearer import JWTBearer, token_required
from ..database import get_session
from ..models import Sala

router = APIRouter(prefix="/api/v1/salas", tags=["Salas"])


@router.get("/")
@token_required
async def obter_salas(
    skip: int = 0,
    count: int = 10,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sequence[Sala]:
    return session.exec(select(Sala).offset(skip).limit(count)).all()


@router.get("/{id}")
@token_required
async def obter_sala(
    id: int,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sala:
    sala = session.exec(select(Sala).where(Sala.id == id)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrado")

    return sala


@router.post("/")
@token_required
async def criar_sala(
    sala: Sala,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sala:
    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.patch("/{id}")
@token_required
async def editar_sala(
    id: int,
    sala: Sala,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sala:
    sala_antiga = session.exec(select(Sala).where(Sala.id == id)).first()

    if not sala_antiga:
        raise HTTPException(404, "Sala nao foi encontrado")

    sala.id = sala_antiga.id

    session.add(sala)
    session.commit()
    session.refresh(sala)

    return sala


@router.delete("/{id}")
@token_required
async def deletar_sala(
    id: int,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
):
    sala = session.exec(select(Sala).where(Sala.id == id)).first()

    if not sala:
        raise HTTPException(404, "Sala nao foi encontrada")

    session.delete(sala)
    session.commit()

    return {"mensagem": "Sala deletada com sucesso"}
