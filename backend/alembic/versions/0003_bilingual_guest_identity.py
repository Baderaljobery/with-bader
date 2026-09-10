"""Add bilingual guest name + research public_appearances/identity_confidence.

Purely additive: every new column is nullable so existing (legacy) guest
and guest_research rows need no backfill and no fabricated translations.
GuestCreate enforces name_ar/name_en as required for NEW guests at the
Pydantic layer (app/schemas/guest.py) - not at the DB level, so this
migration never has to touch existing data.

Only the guest NAME is bilingual - job_title/company/biography stay the
single-value columns they always were (an earlier local draft of this
migration also added job_title_ar/en, company_ar/en, industry_ar/en,
country, biography_ar/en; that was based on a misreading of the actual
requirement and was corrected here before ever being committed/shared).

Revision ID: 0003_bilingual_guest_identity
Revises: 0002_require_guest_owner
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003_bilingual_guest_identity"
down_revision = "0002_require_guest_owner"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("guests", sa.Column("name_ar", sa.Text(), nullable=True))
    op.add_column("guests", sa.Column("name_en", sa.Text(), nullable=True))

    op.add_column(
        "guest_research",
        sa.Column("public_appearances", JSONB(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "guest_research",
        sa.Column("identity_confidence", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("guest_research", "identity_confidence")
    op.drop_column("guest_research", "public_appearances")
    op.drop_column("guests", "name_en")
    op.drop_column("guests", "name_ar")
