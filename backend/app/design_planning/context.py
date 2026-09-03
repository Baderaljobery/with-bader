import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.design_planning.models import PlanContextItem
from app.models.block import Block
from app.models.notebook import Notebook
from app.models.notebook_page import NotebookPage
from app.models.question import Question
from app.services import content_service

# Same text-like block types Content Creation's context builder pulls from
# (see app/content/generation/context_builder.py) - structural block types
# (divider/bullet_list/checklist/...) carry no narrative text worth
# planning slides from.
_NOTEBOOK_TEXT_BLOCK_TYPES = (
    "content_idea",
    "personal_note",
    "highlight",
    "quote",
    "question",
    "answer",
    "paragraph",
    "heading",
    "callout",
)


def _block_text(content: object) -> str | None:
    if not isinstance(content, dict):
        return None
    text = content.get("text")
    return text.strip() if isinstance(text, str) and text.strip() else None


def gather_slide_planning_context(
    db: Session,
    guest_id: uuid.UUID,
    content_draft_id: uuid.UUID | None,
    question_ids: list[uuid.UUID],
    notebook_block_ids: list[uuid.UUID],
) -> list[PlanContextItem]:
    """Assembles ONLY explicitly user-selected, real source material - see
    Part 6/7 of the Design Engine rework spec: no automatic inclusion of
    everything, no re-running research, unanswered questions are never
    treated as facts. Priority order in the returned list: content draft,
    then selected answered Q&A, then selected notebook blocks."""
    items: list[PlanContextItem] = []

    if content_draft_id is not None:
        draft = content_service.get_content_draft_by_id(db, content_draft_id)
        if draft.guest_id != guest_id:
            raise content_service.ContentDraftNotFoundError(
                f"Content draft '{content_draft_id}' not found for guest '{guest_id}'"
            )
        text = f"{draft.title}\n{draft.content}" if draft.title else draft.content
        items.append(PlanContextItem(id="C1", category="content_draft", text=text))

    if question_ids:
        stmt = select(Question).where(
            Question.id.in_(question_ids),
            Question.guest_id == guest_id,
            Question.answer_status == "answered",
            Question.answer.is_not(None),
        )
        # Unanswered/mismatched-guest ids are silently dropped, never used
        # as facts - same grounding rule as every other AI feature here.
        by_id = {str(q.id): q for q in db.scalars(stmt).all()}
        ordered = [by_id[str(qid)] for qid in question_ids if str(qid) in by_id]
        for index, question in enumerate(ordered, start=1):
            items.append(
                PlanContextItem(
                    id=f"A{index}", category="answers", text=f"Q: {question.text_}\nA: {question.answer}"
                )
            )

    if notebook_block_ids:
        stmt = (
            select(Block)
            .join(NotebookPage, Block.page_id == NotebookPage.id)
            .join(Notebook, NotebookPage.notebook_id == Notebook.id)
            .where(
                Block.id.in_(notebook_block_ids),
                Notebook.guest_id == guest_id,
                Block.type.in_(_NOTEBOOK_TEXT_BLOCK_TYPES),
            )
        )
        by_id = {str(b.id): b for b in db.scalars(stmt).all()}
        ordered = [by_id[str(bid)] for bid in notebook_block_ids if str(bid) in by_id]
        notebook_index = 0
        for block in ordered:
            text = _block_text(block.content)
            if not text:
                continue
            notebook_index += 1
            items.append(
                PlanContextItem(id=f"N{notebook_index}", category="notebook", text=f"[{block.type}] {text}")
            )

    return items


def has_sufficient_context(items: list[PlanContextItem]) -> bool:
    """Every item that reaches this function is already real, selected
    source material (no "topic hint only" category exists here) - so any
    non-empty selection counts as sufficient."""
    return len(items) > 0
