from typing import Sequence

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
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sequence[Usuario]:
    return session.exec(select(Usuario)).all()


@router.get("/{username}")
@token_required
async def obter_usuarios_expecifico(
    username: str,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
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
    skip: int = 0,
    count: int = 10,
    dependencies: JWTBearer = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Sequence[tuple[Reserva, Sala]]:
    usuario = session.exec(
        select(Token.id_usuario).where(Token.access_token == dependencies)
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
    usuario: Usuario, session: Session = Depends(get_session)
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
    request: RequestData, session: Session = Depends(get_session)
) -> dict[str, str]:
    usuario = session.exec(
        select(Usuario).where(Usuario.email == request.email)
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email errado",
        )

    hashed_password = usuario.senha
    if not verify_password(request.senha, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Senha errada",
        )

    access = create_access_token(str(usuario.id))
    refresh = create_refresh_token(str(usuario.id))

    token = Token(
        id_usuario=usuario.id,  # type: ignore
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
    dependencies: str | bytes = Depends(JWTBearer()),
    session: Session = Depends(get_session),
) -> Resposta:
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = int(payload["sub"])
    token_record = session.exec(select(Token)).all()
    info: list[int] = []
    for record in token_record:
        print("record", record)
        if (Instant.now().py_datetime() - record.data_criacao).days > 1:
            info.append(record.id_usuario)
    if info:
        existing_token = session.exec(
            select(Token).where(Token.id_usuario in info)
        ).first()
        session.delete(existing_token)
        session.commit()

    existing_token = session.exec(
        select(Token).where(
            Token.id_usuario == user_id,
            Token.access_token == token,
        )
    ).first()

    if existing_token:
        existing_token.status = False
        session.add(existing_token)
        session.commit()
        session.refresh(existing_token)
    return mensagem("Logout bem sucessido")


@router.post("/alterar-senha")
async def alterar_senha(
    request: ChangePassword, session: Session = Depends(get_session)
):
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
