import unittest

from app.database.session import SessionLocal
from app.main import app
from app.schemas.block import BlockCreate
from app.schemas.guest import GuestCreate
from app.schemas.notebook import NotebookCreate
from app.schemas.notebook_page import NotebookPageCreate
from app.services import block_service, notebook_page_service, notebook_service
from app.services.guest_service import create_guest, delete_guest

from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()


class GuestNotebookBlocksTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Guest Notebook Blocks Test Guest"), created_by=client.user_id)
        self.notebook = notebook_service.create_notebook(self.db, self.guest.id, NotebookCreate(title="N"))
        self.page = notebook_page_service.create_notebook_page(
            self.db, self.notebook.id, NotebookPageCreate(title="P", position=0)
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_text_like_blocks_are_listed(self):
        block_service.create_block(
            self.db, self.page.id, BlockCreate(type="content_idea", content={"text": "فكرة"}, position=0)
        )
        response = client.get(f"/api/guests/{self.guest.id}/notebook-blocks")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["type"], "content_idea")

    def test_structural_blocks_are_excluded(self):
        block_service.create_block(self.db, self.page.id, BlockCreate(type="divider", content={}, position=0))
        response = client.get(f"/api/guests/{self.guest.id}/notebook-blocks")
        self.assertEqual(response.json(), [])

    def test_returns_404_for_unknown_guest(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/guests/{fake_id}/notebook-blocks")
        self.assertEqual(response.status_code, 404)

    def test_blocks_from_other_guests_are_excluded(self):
        other_guest = create_guest(self.db, GuestCreate(name="Other Guest"), created_by=client.user_id)
        try:
            other_notebook = notebook_service.create_notebook(self.db, other_guest.id, NotebookCreate(title="N2"))
            other_page = notebook_page_service.create_notebook_page(
                self.db, other_notebook.id, NotebookPageCreate(title="P2", position=0)
            )
            block_service.create_block(
                self.db, other_page.id, BlockCreate(type="content_idea", content={"text": "آخر"}, position=0)
            )
            response = client.get(f"/api/guests/{self.guest.id}/notebook-blocks")
            self.assertEqual(response.json(), [])
        finally:
            delete_guest(self.db, other_guest.id)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
