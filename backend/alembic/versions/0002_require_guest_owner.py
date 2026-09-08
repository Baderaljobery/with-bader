"""Require every guest to have an owner.

Revision ID: 0002_require_guest_owner
Revises: 0001_legacy_009
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_require_guest_owner"
down_revision = "0001_legacy_009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    ownerless_count = connection.scalar(
        sa.text("SELECT count(*) FROM guests WHERE created_by IS NULL")
    )
    if ownerless_count:
        raise RuntimeError(
            f"Cannot require guest ownership: {ownerless_count} guest row(s) have no owner. "
            "Assign each row to a verified user before retrying; this migration will not guess."
        )
    op.alter_column("guests", "created_by", existing_type=sa.UUID(), nullable=False)


def downgrade() -> None:
    op.alter_column("guests", "created_by", existing_type=sa.UUID(), nullable=True)
