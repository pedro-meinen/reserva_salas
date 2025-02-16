from fastapi import FastAPI, Response

from .routes.reservas import router as router_reservas
from .routes.salas import router as router_salas

app = FastAPI()
app.include_router(router_reservas)
app.include_router(router_salas)


@app.get("/")
async def root() -> Response:
    return Response("servidor rodando!")
