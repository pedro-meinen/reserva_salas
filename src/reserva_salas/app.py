from fastapi import FastAPI

from .routes.reservas import router as router_reservas
from .routes.salas import router as router_salas
from .routes.usuarios import router as router_usuarios
from .schemas import Resposta, mensagem

app = FastAPI()
app.include_router(router_reservas)
app.include_router(router_salas)
app.include_router(router_usuarios)


@app.get("/")
async def root() -> Resposta:
    return mensagem("Servidor Rodando")
