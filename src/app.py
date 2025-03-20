from fastapi import FastAPI

from src.auth import auth
from src.routes.reservas import router as router_reservas
from src.routes.salas import router as router_salas
from src.routes.usuarios import router as router_usuarios
from src.schemas import Resposta, mensagem

app = FastAPI()
app.include_router(router_reservas)
app.include_router(router_salas)
app.include_router(router_usuarios)

auth.handle_errors(app)


@app.get("/")
async def root() -> Resposta:
    return mensagem("Servidor Rodando")
