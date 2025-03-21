from starlette_admin.contrib.sqlmodel import Admin, ModelView

from src.database import engine
from src.models import Reserva, Sala, Usuario

admin = Admin(engine, title="Reserva de Salas")

admin.add_view(ModelView(Usuario))
admin.add_view(ModelView(Sala))
admin.add_view(ModelView(Reserva))
