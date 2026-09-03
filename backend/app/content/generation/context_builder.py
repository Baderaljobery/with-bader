import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.generation.models import ContentContextItem
from app.core.config import settings
from app.models.block import Block
from app.models.notebook import Notebook
from app.models.notebook_page import NotebookPage
from app.models.question import Question
from app.services import guest_research_service, guest_transcript_service

# Block types the notebook feature actually lets users create for ideas/
# notes/highlights (see frontend/features/notebook/lib/block-types.ts) -
# structural types like divider/bullet_list/checklist carry no narrative
# text worth pulling into a content draft.
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

_RESEARCH_FIELDS = (
    "career_history",
    "achievements",
    "projects",
    "interesting_events",
    "potential_interview_angles",
)

# Categories that count as *meaningful* grounding for a "may we generate?"
# decision. "questions" alone (unanswered question text - a topic hint,
# never a fact) is deliberately excluded - see build_content_context's
# docstring.
MEANINGFUL_CATEGORIES = frozenset({"answers", "notebook", "transcript", "research"})


def _block_text(content: object) -> str | None:
    """Mirrors the frontend's own block-content convention (see
    frontend/features/notebook/lib/block-content.ts): text-like block types
    store {"text": "..."} - read defensively, never invented here, since
    the backend enforces no shape on this JSONB column."""
    if not isinstance(content, dict):
        return None
    text = content.get("text")
    return text.strip() if isinstance(text, str) and text.strip() else None


def _research_fact(item: object) -> str | None:
    if not isinstance(item, dict):
        return None
    parts = [
        str(item[key]).strip()
        for key in ("title", "role", "company", "description", "why_interesting", "reason")
        if item.get(key)
    ]
    return " - ".join(parts) if parts else None


def _bound_by_chars(items: list[ContentContextItem], max_chars: int) -> list[ContentContextItem]:
    bounded: list[ContentContextItem] = []
    total = 0
    for item in items:
        total += len(item.text)
        if bounded and total > max_chars:
            break
        bounded.append(item)
    return bounded


def build_content_context(db: Session, guest_id: uuid.UUID) -> list[ContentContextItem]:
    """Assembles a bounded, priority-ordered grounding context from the
    guest's ALREADY-EXISTING data - never performs new research, browsing,
    or search (research is read from the latest completed GuestResearch
    row only; Exa/Tavily are never called here).

    Priority order (highest first): answered interview questions, notebook
    ideas/notes/highlights, transcript excerpts (supporting evidence,
    length-capped), research facts, saved questions as light topic hints.

    Unanswered questions are never treated as factual content: they only
    ever contribute their own question TEXT via the final "questions"
    category, never a fabricated answer - see MEANINGFUL_CATEGORIES for how
    callers should decide whether this context is "enough" to generate on.
    """
    items: list[ContentContextItem] = []

    # 1. Answered interview questions - the strongest, most factual source.
    answered_stmt = (
        select(Question)
        .where(
            Question.guest_id == guest_id,
            Question.answer_status == "answered",
            Question.answer.is_not(None),
        )
        .order_by(Question.answer_updated_at.desc().nullslast())
        .limit(settings.content_generation_max_answers)
    )
    for index, question in enumerate(db.scalars(answered_stmt).all(), start=1):
        items.append(
            ContentContextItem(
                id=f"A{index}",
                category="answers",
                text=f"Q: {question.text_}\nA: {question.answer}",
            )
        )

    # 2. Notebook content the user deliberately wrote as ideas/notes/quotes.
    notebook_stmt = (
        select(Block)
        .join(NotebookPage, Block.page_id == NotebookPage.id)
        .join(Notebook, NotebookPage.notebook_id == Notebook.id)
        .where(Notebook.guest_id == guest_id, Block.type.in_(_NOTEBOOK_TEXT_BLOCK_TYPES))
        .order_by(Block.updated_at.desc())
        .limit(settings.content_generation_max_notebook_blocks)
    )
    notebook_index = 0
    for block in db.scalars(notebook_stmt).all():
        text = _block_text(block.content)
        if not text:
            continue
        notebook_index += 1
        items.append(
            ContentContextItem(id=f"N{notebook_index}", category="notebook", text=f"[{block.type}] {text}")
        )

    # 3. Transcript excerpt - supporting evidence only, length-bounded and
    # never dumped in full (Q&A and notebook data are preferred).
    transcript = guest_transcript_service.get_guest_transcript(db, guest_id)
    if transcript is not None and transcript.text_.strip():
        excerpt = transcript.text_.strip()[: settings.content_generation_max_transcript_chars]
        items.append(ContentContextItem(id="T1", category="transcript", text=excerpt))

    # 4. Research facts from the latest completed GuestResearch only.
    research = guest_research_service.get_latest_guest_research(db, guest_id)
    if research is not None:
        research_index = 0
        for field_name in _RESEARCH_FIELDS:
            for raw in getattr(research, field_name, None) or []:
                if research_index >= settings.content_generation_max_research_items:
                    break
                fact = _research_fact(raw)
                if fact:
                    research_index += 1
                    items.append(ContentContextItem(id=f"R{research_index}", category="research", text=fact))

    # 5. Saved questions as light topic hints only - never a source of facts.
    questions_stmt = (
        select(Question)
        .where(Question.guest_id == guest_id)
        .order_by(Question.position.asc())
        .limit(settings.content_generation_max_questions)
    )
    for index, question in enumerate(db.scalars(questions_stmt).all(), start=1):
        items.append(ContentContextItem(id=f"Q{index}", category="questions", text=question.text_))

    return _bound_by_chars(items, settings.content_generation_max_input_chars)


def has_meaningful_context(items: list[ContentContextItem]) -> bool:
    """True if at least one item comes from a real evidentiary category -
    "questions" alone (unanswered question text) is not enough to generate
    confident content from."""
    return any(item.category in MEANINGFUL_CATEGORIES for item in items)
