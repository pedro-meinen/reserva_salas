from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.admin import admin
from src.auth import auth
from src.routes.reservas import router as router_reservas
from src.routes.salas import router as router_salas
from src.routes.usuarios import router as router_usuarios
from src.schemas import Resposta, mensagem


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:  # noqa: RUF029
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router_reservas)
app.include_router(router_salas)
app.include_router(router_usuarios)

auth.handle_errors(app)

admin.mount_to(app)


@app.get("/")
async def root() -> Resposta:
    return mensagem("Servidor Rodando")
