"""
Ajustando modelos para alterar a forma como os endpoints buscam os dados.

Revision ID: ff6f1dbde8bd
Revises: 4fa82975ba25
Create Date: 2025-02-19 13:49:09.876672

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ff6f1dbde8bd"
down_revision: str | None = "4fa82975ba25"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("reserva", schema=None) as batch_op:
        batch_op.alter_column(
            "reservado_por",
            existing_type=sa.VARCHAR(length=50),
            type_=sa.Integer(),
            nullable=True,
        )
        batch_op.create_foreign_key(
            "fx_reservado_por", "usuario", ["reservado_por"], ["id"]
        )

    with op.batch_alter_table("usuario", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_usuario_email"), ["email"], unique=True
        )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("usuario", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_usuario_email"))

    with op.batch_alter_table("reserva", schema=None) as batch_op:
        batch_op.drop_constraint("fx_reservado_por", type_="foreignkey")
        batch_op.alter_column(
            "reservado_por",
            existing_type=sa.Integer(),
            type_=sa.VARCHAR(length=50),
            nullable=False,
        )

    # ### end Alembic commands ###
