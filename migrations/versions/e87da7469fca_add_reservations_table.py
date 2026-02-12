"""add reservations table

Revision ID: e87da7469fca
Revises: 9e6e39ff9569
Create Date: 2026-02-12 14:29:10.204260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e87da7469fca'
down_revision: Union[str, Sequence[str], None] = '9e6e39ff9569'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),

        sa.Column("type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="planned"),

        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column("confirmation_code", sa.String(length=80), nullable=True),

        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=True),

        sa.Column("location_text", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),

        sa.Column("estimated_cost_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("estimated_cost_currency", sa.String(length=3), nullable=False, server_default="USD"),

        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_reservations_trip_start_at", "reservations", ["trip_id", "start_at"])
    op.create_index("ix_reservations_trip_type", "reservations", ["trip_id", "type"])
    op.create_index("ix_reservations_trip_status", "reservations", ["trip_id", "status"])

    op.create_check_constraint(
        "ck_reservations_end_after_start",
        "reservations",
        "(start_at IS NULL) OR (end_at IS NULL) OR (end_at >= start_at)",
    )
    op.create_check_constraint(
        "ck_reservations_estimated_cost_nonnegative",
        "reservations",
        "(estimated_cost_amount IS NULL) OR (estimated_cost_amount >= 0)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_reservations_estimated_cost_nonnegative", "reservations", type_="check")
    op.drop_constraint("ck_reservations_end_after_start", "reservations", type_="check")
    op.drop_index("ix_reservations_trip_status", table_name="reservations")
    op.drop_index("ix_reservations_trip_type", table_name="reservations")
    op.drop_index("ix_reservations_trip_start_at", table_name="reservations")
    op.drop_table("reservations")
