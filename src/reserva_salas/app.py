from fastapi import FastAPI, Response

from .routes.reservas import router as router_reservas
from .routes.salas import router as router_salas
from .routes.usuarios import router as router_usuarios

app = FastAPI()
app.include_router(router_reservas)
app.include_router(router_salas)
app.include_router(router_usuarios)


@app.get("/")
async def root() -> Response:
    return Response("servidor rodando!")
