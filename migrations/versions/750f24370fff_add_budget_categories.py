"""add budget categories

Revision ID: 750f24370fff
Revises: 3c12f13375dd
Create Date: 2026-02-12 15:34:46.959328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '750f24370fff'
down_revision: Union[str, Sequence[str], None] = '3c12f13375dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    op.create_table(
        "budget_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trip_id", sa.Integer(), sa.ForeignKey("trips.id", ondelete="CASCADE"), nullable=False),

        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("planned_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="USD"),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_index("ix_budget_categories_trip_id", "budget_categories", ["trip_id"])
    op.create_index("ix_budget_categories_trip_name", "budget_categories", ["trip_id", "name"])
    op.create_unique_constraint("uq_budget_categories_trip_name", "budget_categories", ["trip_id", "name"])
    op.create_check_constraint(
        "ck_budget_categories_planned_nonnegative",
        "budget_categories",
        "(planned_amount IS NULL) OR (planned_amount >= 0)",
    )

    # Add category_id to spend_entries
    op.add_column("spend_entries", sa.Column("category_id", sa.Integer(), nullable=True))
    op.create_index("ix_spend_entries_category_id", "spend_entries", ["category_id"])
    op.create_foreign_key(
        "fk_spend_entries_category_id",
        "spend_entries",
        "budget_categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_spend_entries_category_id", "spend_entries", type_="foreignkey")
    op.drop_index("ix_spend_entries_category_id", table_name="spend_entries")
    op.drop_column("spend_entries", "category_id")

    op.drop_constraint("ck_budget_categories_planned_nonnegative", "budget_categories", type_="check")
    op.drop_constraint("uq_budget_categories_trip_name", "budget_categories", type_="unique")
    op.drop_index("ix_budget_categories_trip_name", table_name="budget_categories")
    op.drop_index("ix_budget_categories_trip_id", table_name="budget_categories")
    op.drop_table("budget_categories")

