"""Part 18/42: deleting an account must remove the user and every guest
(and everything beneath it) they own, invalidate their session, and never
touch another user's data."""

import unittest

from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.content_draft import ContentDraftCreate
from app.schemas.guest import GuestCreate
from app.services import content_service, guest_service
from tests.auth_test_helpers import make_authenticated_client


class AccountDeletionTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.client_a = make_authenticated_client("User A - to delete")
        self.client_b = make_authenticated_client("User B - must survive")

        self.guest_a = guest_service.create_guest(
            self.db, GuestCreate(name="ضيف المستخدم أ"), created_by=self.client_a.user_id
        )
        self.draft_a = content_service.create_content_draft(
            self.db, self.guest_a.id, ContentDraftCreate(platform="linkedin", length="short", content="محتوى أ")
        )
        self.guest_b = guest_service.create_guest(
            self.db, GuestCreate(name="ضيف المستخدم ب"), created_by=self.client_b.user_id
        )

    def tearDown(self):
        # User A's row (and cascaded guest/content) should already be gone -
        # only clean up whatever the test didn't already delete.
        for user_id in (self.client_a.user_id, self.client_b.user_id):
            user = self.db.get(User, user_id)
            if user is not None:
                self.db.delete(user)
        self.db.commit()
        self.db.close()

    def test_delete_account_removes_user_and_cascades_to_their_data(self):
        # Capture ids before deleting - expunging the session below detaches
        # guest_a/draft_a, and both were expired by the earlier commit, so
        # reading .id off them afterwards would need a refresh that can't
        # happen on a detached instance.
        guest_a_id = self.guest_a.id
        draft_a_id = self.draft_a.id

        response = self.client_a.delete("/api/auth/account")
        self.assertEqual(response.status_code, 204)

        # expunge (not just expire) the guest_a/draft_a instances this
        # session already holds - a real DB delete of a row still present
        # in the identity map makes a plain expire+refresh raise
        # ObjectDeletedError instead of letting .get() return None.
        self.db.expunge_all()
        self.assertIsNone(self.db.get(User, self.client_a.user_id))
        self.assertIsNone(self.db.get(type(self.guest_a), guest_a_id))
        with self.assertRaises(content_service.ContentDraftNotFoundError):
            content_service.get_content_draft_by_id(self.db, draft_a_id)

    def test_deleted_user_cannot_authenticate_again(self):
        email = self.client_a.email
        password = self.client_a.password
        self.client_a.delete("/api/auth/account")

        login_response = self.client_a.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        # The account no longer exists at all - any login attempt for it
        # fails the same generic way as any other unknown email.
        self.assertEqual(login_response.status_code, 401)

    def test_delete_account_clears_the_session_cookie(self):
        self.client_a.delete("/api/auth/account")
        me_response = self.client_a.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 401)

    def test_user_b_and_their_guest_survive_user_a_deletion(self):
        guest_b_id = self.guest_b.id

        self.client_a.delete("/api/auth/account")

        self.db.expunge_all()
        self.assertIsNotNone(self.db.get(User, self.client_b.user_id))

        response = self.client_b.get(f"/api/guests/{guest_b_id}")
        self.assertEqual(response.status_code, 200)

        me_response = self.client_b.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
