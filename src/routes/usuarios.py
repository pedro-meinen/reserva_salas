from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.auth import (
    AuthXDependency,
    TokenPayload,
    auth,
    get_hashed_password,
    verify_password,
)
from src.database import get_session
from src.models import Reserva, Sala, Usuario
from src.schemas import ChangePassword, LoginData, Resposta, mensagem

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get("/")
async def obter_usuarios(
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Sequence[Usuario]:
    return session.exec(select(Usuario)).all()


@router.get("/{username}")
async def obter_usuarios_especifico(
    username: str,
    _dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
) -> Usuario:
    usuario = session.exec(
        select(Usuario).where(username == Usuario.email)
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario não encontrado",
        )

    return usuario


@router.get("/reservas")
async def obter_reservas_por_usuario(
    dependencies: Annotated[TokenPayload, Depends(auth.access_token_required)],
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[tuple[Reserva, Sala]]:
    usuario = int(dependencies.sub)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não possui permissão para realizar essa operação",
        )

    return session.exec(
        select(Reserva, Sala)
        .where(Reserva.reservado_por == usuario)
        .join(Sala)
        .offset(skip)
        .limit(count)
    ).all()


@router.post("/registrar")
async def registrar_usuario(
    usuario: Usuario, session: Annotated[Session, Depends(get_session)]
) -> Resposta:
    if session.exec(
        select(Usuario).where(Usuario.email == usuario.email)
    ).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario já registrado",
        )

    usuario.senha = get_hashed_password(usuario.senha)

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return mensagem("Usuario registrado com sucesso!")


@router.post("/login")
async def login(
    data: LoginData,
    deps: Annotated[AuthXDependency, Depends(auth.get_dependency)],
    session: Annotated[Session, Depends(get_session)],
) -> Resposta:
    usuario = session.exec(
        select(Usuario).where(Usuario.email == data.email)
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email errado"
        )

    if not verify_password(data.senha, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Senha errada"
        )

    token = deps.create_access_token(str(usuario.id))
    deps.set_access_cookies(token)
    return mensagem("Login bem sucedido")


@router.post("/logout")
async def logout(
    deps: Annotated[AuthXDependency, Depends(auth.get_dependency)],
) -> Resposta:
    deps.unset_access_cookies()
    return mensagem("Logout bem sucedido")


@router.post("/alterar-senha")
async def alterar_senha(
    request: ChangePassword, session: Annotated[Session, Depends(get_session)]
) -> Resposta:
    user = session.exec(
        select(Usuario).where(Usuario.email == request.email)
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )

    if not verify_password(request.senha_antiga, user.senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid old password",
        )

    encrypted_password = get_hashed_password(request.senha_nova)
    user.senha = encrypted_password
    session.commit()

    return mensagem("Senha alterada com sucesso!")
