import unittest

from app.design_planning.context import gather_slide_planning_context, has_sufficient_context
from app.database.session import SessionLocal
from app.schemas.block import BlockCreate
from app.schemas.content_draft import ContentDraftCreate

from app.schemas.notebook import NotebookCreate
from app.schemas.notebook_page import NotebookPageCreate
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import block_service, content_service, notebook_page_service, notebook_service, question_service
from app.services.guest_service import create_guest, delete_guest
from tests.db_test_helpers import create_test_owner, delete_test_owner, make_guest_create

class DesignPlanningContextTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, make_guest_create(name="Design Planning Context Test Guest"), self.owner.id
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    def test_no_selection_is_empty_and_insufficient(self):
        items = gather_slide_planning_context(self.db, self.guest.id, None, [], [])
        self.assertEqual(items, [])
        self.assertFalse(has_sufficient_context(items))

    def test_selected_content_draft_becomes_primary_context(self):
        draft = content_service.create_content_draft(
            self.db,
            self.guest.id,
            ContentDraftCreate(platform="linkedin", length="medium", title="T", content="نص المحتوى الأساسي."),
        )
        items = gather_slide_planning_context(self.db, self.guest.id, draft.id, [], [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].category, "content_draft")
        self.assertIn("نص المحتوى الأساسي.", items[0].text)
        self.assertTrue(has_sufficient_context(items))

    def test_content_draft_from_different_guest_is_rejected(self):
        other_guest = create_guest(self.db, make_guest_create(name="Other Guest"), self.owner.id)
        try:
            other_draft = content_service.create_content_draft(
                self.db, other_guest.id, ContentDraftCreate(platform="linkedin", length="short", content="x")
            )
            with self.assertRaises(content_service.ContentDraftNotFoundError):
                gather_slide_planning_context(self.db, self.guest.id, other_draft.id, [], [])
        finally:
            delete_guest(self.db, other_guest.id)

    def test_only_answered_selected_questions_are_used(self):
        answered = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="سؤال مُجاب؟")
        )
        question_service.set_question_answer(
            self.db, answered.id, QuestionAnswerUpdate(answer="إجابة حقيقية.")
        )
        unanswered = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="سؤال بلا إجابة؟")
        )

        items = gather_slide_planning_context(
            self.db, self.guest.id, None, [answered.id, unanswered.id], []
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].category, "answers")
        self.assertIn("إجابة حقيقية.", items[0].text)
        self.assertTrue(has_sufficient_context(items))

    def test_selected_notebook_block_becomes_context(self):
        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block = block_service.create_block(
            self.db, page.id, BlockCreate(type="content_idea", content={"text": "فكرة محتوى مهمة"}, position=0)
        )

        items = gather_slide_planning_context(self.db, self.guest.id, None, [], [block.id])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].category, "notebook")
        self.assertIn("فكرة محتوى مهمة", items[0].text)
        self.assertTrue(has_sufficient_context(items))

    def test_unselected_notebook_block_is_not_included(self):
        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block_service.create_block(
            self.db, page.id, BlockCreate(type="content_idea", content={"text": "لم يتم اختياره"}, position=0)
        )

        items = gather_slide_planning_context(self.db, self.guest.id, None, [], [])
        self.assertEqual(items, [])

    def test_priority_order_content_draft_then_answers_then_notebook(self):
        draft = content_service.create_content_draft(
            self.db, self.guest.id, ContentDraftCreate(platform="linkedin", length="short", content="محتوى")
        )
        question = question_service.create_question(self.db, self.guest.id, QuestionCreate(text="س؟"))
        question_service.set_question_answer(self.db, question.id, QuestionAnswerUpdate(answer="ج"))
        notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        page = notebook_page_service.create_notebook_page(
            self.db, notebook.id, NotebookPageCreate(title="P", position=0)
        )
        block = block_service.create_block(
            self.db, page.id, BlockCreate(type="personal_note", content={"text": "ملاحظة"}, position=0)
        )

        items = gather_slide_planning_context(
            self.db, self.guest.id, draft.id, [question.id], [block.id]
        )
        self.assertEqual([item.category for item in items], ["content_draft", "answers", "notebook"])

if __name__ == "__main__":
    unittest.main()
