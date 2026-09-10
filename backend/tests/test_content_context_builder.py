import unittest

from app.content.generation.context_builder import build_content_context, has_meaningful_context
from app.core.config import settings
from app.database.session import SessionLocal
from app.schemas.block import BlockCreate

from app.schemas.guest_research import GuestResearchCreate
from app.schemas.guest_transcript import GuestTranscriptCreate
from app.schemas.notebook import NotebookCreate
from app.schemas.notebook_page import NotebookPageCreate
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import (
    block_service,
    guest_research_service,
    guest_transcript_service,
    notebook_page_service,
    notebook_service,
    question_service,
)
from app.services.guest_service import create_guest, delete_guest
from tests.db_test_helpers import create_test_owner, delete_test_owner, make_guest_create

class ContentContextBuilderTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, make_guest_create(name="Context Builder Test Guest"), self.owner.id
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    def test_empty_guest_has_no_meaningful_context(self):
        items = build_content_context(self.db, self.guest.id)
        self.assertEqual(items, [])
        self.assertFalse(has_meaningful_context(items))

    def test_unanswered_question_only_contributes_topic_hint_not_meaningful(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="Unanswered question?")
        )
        items = build_content_context(self.db, self.guest.id)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].category, "questions")
        self.assertFalse(has_meaningful_context(items))

    def test_answered_question_becomes_answers_category_and_is_meaningful(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        question_service.set_question_answer(
            self.db, question.id, QuestionAnswerUpdate(answer="Funding was the hardest part.")
        )

        items = build_content_context(self.db, self.guest.id)
        answer_items = [item for item in items if item.category == "answers"]
        self.assertEqual(len(answer_items), 1)
        self.assertIn("Funding was the hardest part.", answer_items[0].text)
        self.assertTrue(has_meaningful_context(items))
        # The same question also appears via the "questions" topic-hint
        # pass - never duplicated as a second fabricated fact.
        self.assertEqual(len([item for item in items if item.category == "questions"]), 1)

    def test_notebook_content_idea_block_becomes_notebook_category(self):
        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block_service.create_block(
            self.db,
            page.id,
            BlockCreate(type="content_idea", content={"text": "Talk about the pivot moment"}, position=0),
        )

        items = build_content_context(self.db, self.guest.id)
        notebook_items = [item for item in items if item.category == "notebook"]
        self.assertEqual(len(notebook_items), 1)
        self.assertIn("Talk about the pivot moment", notebook_items[0].text)
        self.assertTrue(has_meaningful_context(items))

    def test_structural_block_types_are_ignored(self):
        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block_service.create_block(self.db, page.id, BlockCreate(type="divider", content={}, position=0))
        block_service.create_block(
            self.db, page.id, BlockCreate(type="bullet_list", content={"items": ["a", "b"]}, position=1)
        )

        items = build_content_context(self.db, self.guest.id)
        self.assertEqual([item for item in items if item.category == "notebook"], [])
        self.assertFalse(has_meaningful_context(items))

    def test_transcript_becomes_bounded_context_item(self):
        guest_transcript_service.create_guest_transcript(
            self.db,
            self.guest.id,
            GuestTranscriptCreate(text="x" * 20000, stt_provider="cohere", stt_model="test"),
        )

        items = build_content_context(self.db, self.guest.id)
        transcript_items = [item for item in items if item.category == "transcript"]
        self.assertEqual(len(transcript_items), 1)
        self.assertLessEqual(
            len(transcript_items[0].text), settings.content_generation_max_transcript_chars
        )
        self.assertTrue(has_meaningful_context(items))

    def test_research_facts_become_research_category(self):
        guest_research_service.create_guest_research(
            self.db,
            self.guest.id,
            GuestResearchCreate(achievements=[{"title": "Founded Example Co"}]),
        )
        items = build_content_context(self.db, self.guest.id)
        research_items = [item for item in items if item.category == "research"]
        self.assertEqual(len(research_items), 1)
        self.assertIn("Founded Example Co", research_items[0].text)
        self.assertTrue(has_meaningful_context(items))

    def test_priority_order_across_all_categories(self):
        question = question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Q1?"))
        question_service.set_question_answer(self.db, question.id, QuestionAnswerUpdate(answer="A1"))

        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block_service.create_block(
            self.db, page.id, BlockCreate(type="personal_note", content={"text": "note"}, position=0)
        )

        guest_transcript_service.create_guest_transcript(
            self.db, self.guest.id, GuestTranscriptCreate(text="transcript text", stt_provider="cohere", stt_model="t")
        )
        guest_research_service.create_guest_research(
            self.db, self.guest.id, GuestResearchCreate(achievements=[{"title": "Achievement"}])
        )
        question_service.create_question(self.db, self.guest.id, QuestionCreate(text="Unanswered hint?"))

        items = build_content_context(self.db, self.guest.id)
        categories = [item.category for item in items]

        self.assertLess(categories.index("answers"), categories.index("notebook"))
        self.assertLess(categories.index("notebook"), categories.index("transcript"))
        self.assertLess(categories.index("transcript"), categories.index("research"))
        self.assertLess(categories.index("research"), categories.index("questions"))

if __name__ == "__main__":
    unittest.main()
