"""Persist question-generation intent/provenance and exact dedupe guards.

Revision ID: 0004_question_generation_dedup
Revises: 0003_bilingual_guest_identity
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision = "0004_question_generation_dedup"
down_revision = "0003_bilingual_guest_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("category", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("priority", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("intent_summary", sa.Text(), nullable=True))
    op.add_column(
        "questions",
        sa.Column(
            "research_id",
            UUID(as_uuid=True),
            sa.ForeignKey("guest_research.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("questions", sa.Column("research_version", sa.Integer(), nullable=True))
    op.add_column(
        "questions",
        sa.Column("research_item_ids", JSONB(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "questions",
        sa.Column("source_urls", JSONB(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "questions",
        sa.Column("follow_up_questions", JSONB(), nullable=False, server_default="[]"),
    )
    op.add_column("questions", sa.Column("generation_reason", sa.Text(), nullable=True))
    op.add_column(
        "questions", sa.Column("generation_run_id", UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "questions", sa.Column("generation_candidate_id", UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "questions", sa.Column("ai_normalized_text_hash", sa.Text(), nullable=True)
    )

    # Legacy rows intentionally remain unhashed. The service still compares
    # against them, while this partial index is a concurrency guard for every
    # newly saved AI-generated question without affecting manual questions.
    op.create_index(
        "uq_questions_guest_ai_text_hash",
        "questions",
        ["guest_id", "ai_normalized_text_hash"],
        unique=True,
        postgresql_where=sa.text(
            "source = 'ai_generated' AND ai_normalized_text_hash IS NOT NULL"
        ),
    )
    op.create_index(
        "uq_questions_generation_candidate_id",
        "questions",
        ["generation_candidate_id"],
        unique=True,
        postgresql_where=sa.text("generation_candidate_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_questions_generation_candidate_id", table_name="questions")
    op.drop_index("uq_questions_guest_ai_text_hash", table_name="questions")
    op.drop_column("questions", "ai_normalized_text_hash")
    op.drop_column("questions", "generation_candidate_id")
    op.drop_column("questions", "generation_run_id")
    op.drop_column("questions", "generation_reason")
    op.drop_column("questions", "follow_up_questions")
    op.drop_column("questions", "source_urls")
    op.drop_column("questions", "research_item_ids")
    op.drop_column("questions", "research_version")
    op.drop_column("questions", "research_id")
    op.drop_column("questions", "intent_summary")
    op.drop_column("questions", "priority")
    op.drop_column("questions", "category")
