from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_profiler import PyInstrumentProfilerMiddleware
from redis import asyncio as aioredis

from src.admin import admin
from src.auth import auth
from src.routes import router_reservas, router_salas, router_usuarios
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

app.add_middleware(PyInstrumentProfilerMiddleware)

auth.handle_errors(app)

admin.mount_to(app)


@app.get("/")
async def root() -> Resposta:
    return mensagem("Servidor Rodando")
