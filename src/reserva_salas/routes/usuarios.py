from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlmodel import Session, select
from whenever import Instant

from ..auth import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)
from ..bearer import JWTBearer, token_required
from ..database import get_session
from ..models import Reserva, Sala, Token, Usuario
from ..schemas import (
    ChangePassword,
    RequestData,
    Resposta,
    TokenSchema,
    mensagem,
)
from ..settings import ALGORITHM, JWT_SECRET_KEY

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])


@router.get("/")
@token_required
async def obter_usuarios(
    dependencies: Annotated[JWTBearer, Depends(JWTBearer())],  # noqa: ARG001
    session: Annotated[Session, Depends(get_session)],
) -> Sequence[Usuario]:
    return session.exec(select(Usuario)).all()


@router.get("/{username}")
@token_required
async def obter_usuarios_especifico(
    username: str,
    dependencies: Annotated[JWTBearer, Depends(JWTBearer())],  # noqa: ARG001
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
@token_required
async def obter_reservas_por_usuario(
    dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
    skip: int = 0,
    count: int = 10,
) -> Sequence[tuple[Reserva, Sala]]:
    usuario = session.exec(
        select(Token.id_usuario).where(Token.access_token == str(dependencies))
    ).first()

    if not usuario:
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
    usuario_existente = session.exec(
        select(Usuario).where(Usuario.email == usuario.email)
    ).first()

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario já registrado",
        )

    encrypt_password = get_hashed_password(usuario.senha)

    usuario.senha = encrypt_password

    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    return mensagem("Usuario registrado com sucesso!")


@router.post("/login", response_model=TokenSchema)
async def login(
    request: RequestData, session: Annotated[Session, Depends(get_session)]
) -> dict[str, str]:
    usuario = session.exec(
        select(Usuario).where(Usuario.email == request.email)
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email errado"
        )

    hashed_password = usuario.senha
    if not verify_password(request.senha, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Senha errada"
        )

    access = create_access_token(str(usuario.id))
    refresh = create_refresh_token(str(usuario.id))

    token = Token(
        id_usuario=usuario.id or 0,
        access_token=access,
        refresh_token=refresh,
        status=True,
    )

    session.add(token)
    session.commit()
    session.refresh(token)

    return {"access_token": access, "refresh_token": refresh}


@router.post("/logout")
async def logout(
    dependencies: Annotated[JWTBearer, Depends(JWTBearer())],
    session: Annotated[Session, Depends(get_session)],
) -> Resposta:
    token = str(dependencies)
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = int(payload["sub"])
    token_record = session.exec(select(Token)).all()
    info = [
        record.id_usuario
        for record in token_record
        if (Instant.now().py_datetime() - record.data_criacao).days > 1
    ]
    if info:
        existing_token = session.exec(
            select(Token).where(Token.id_usuario in info)
        ).first()
        session.delete(existing_token)
        session.commit()

    existing_token = session.exec(
        select(Token).where(
            Token.id_usuario == user_id, Token.access_token == token
        )
    ).first()

    if existing_token:
        existing_token.status = False
        session.add(existing_token)
        session.commit()
        session.refresh(existing_token)
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
