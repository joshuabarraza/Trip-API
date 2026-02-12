"""add spend entries

Revision ID: 3c12f13375dd
Revises: e87da7469fca
Create Date: 2026-02-12 15:11:28.059257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c12f13375dd'
down_revision: Union[str, Sequence[str], None] = 'e87da7469fca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.create_table(
        "spend_entries",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reservation_id", sa.Integer(), sa.ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True),

        sa.Column("kind", sa.String(length=16), nullable=False, server_default="expense"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),

        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("description", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_check_constraint(
        "ck_spend_entries_amount_nonnegative",
        "spend_entries",
        "amount >= 0",
    )

    op.create_index("ix_spend_entries_trip_occurred_at", "spend_entries", ["trip_id", "occurred_at"])
    op.create_index("ix_spend_entries_trip_currency", "spend_entries", ["trip_id", "currency"])
    op.create_index("ix_spend_entries_trip_kind", "spend_entries", ["trip_id", "kind"])
    op.create_index("ix_spend_entries_trip_id", "spend_entries", ["trip_id"])
    op.create_index("ix_spend_entries_reservation_id", "spend_entries", ["reservation_id"])


def downgrade() -> None:
    op.drop_index("ix_spend_entries_reservation_id", table_name="spend_entries")
    op.drop_index("ix_spend_entries_trip_id", table_name="spend_entries")
    op.drop_index("ix_spend_entries_trip_kind", table_name="spend_entries")
    op.drop_index("ix_spend_entries_trip_currency", table_name="spend_entries")
    op.drop_index("ix_spend_entries_trip_occurred_at", table_name="spend_entries")
    op.drop_constraint("ck_spend_entries_amount_nonnegative", "spend_entries", type_="check")
    op.drop_table("spend_entries")
