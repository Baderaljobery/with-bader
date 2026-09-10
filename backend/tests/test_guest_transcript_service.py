import unittest

from app.database.session import SessionLocal

from app.schemas.guest_transcript import GuestTranscriptCreate
from app.services import guest_transcript_service
from app.services.guest_service import create_guest, delete_guest
from app.services.guest_transcript_service import (
    GuestTranscriptAlreadyExistsError,
    GuestTranscriptNotFoundError,
)
from tests.db_test_helpers import create_test_owner, delete_test_owner, make_guest_create

class GuestTranscriptServiceTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.owner = create_test_owner(self.db)
        self.guest = create_guest(
            self.db, make_guest_create(name="Transcript Service Test Guest"), self.owner.id
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        delete_test_owner(self.db, self.owner)
        self.db.close()

    def test_create_transcript(self):
        transcript = guest_transcript_service.create_guest_transcript(
            self.db,
            self.guest.id,
            GuestTranscriptCreate(text="Hello world", stt_provider="cohere", stt_model="test-model"),
        )
        self.assertEqual(transcript.text_, "Hello world")
        self.assertEqual(transcript.stt_provider, "cohere")
        self.assertEqual(transcript.guest_id, self.guest.id)

    def test_get_transcript_returns_none_when_missing(self):
        self.assertIsNone(guest_transcript_service.get_guest_transcript(self.db, self.guest.id))

    def test_get_transcript_or_raise_raises_when_missing(self):
        with self.assertRaises(GuestTranscriptNotFoundError):
            guest_transcript_service.get_guest_transcript_or_raise(self.db, self.guest.id)

    def test_second_create_without_replace_existing_raises_conflict(self):
        guest_transcript_service.create_guest_transcript(
            self.db, self.guest.id, GuestTranscriptCreate(text="First version")
        )
        with self.assertRaises(GuestTranscriptAlreadyExistsError):
            guest_transcript_service.create_guest_transcript(
                self.db, self.guest.id, GuestTranscriptCreate(text="Second version")
            )

    def test_replace_existing_true_replaces_text(self):
        first = guest_transcript_service.create_guest_transcript(
            self.db, self.guest.id, GuestTranscriptCreate(text="First version")
        )
        second = guest_transcript_service.create_guest_transcript(
            self.db,
            self.guest.id,
            GuestTranscriptCreate(text="Second version", stt_provider="cohere"),
            replace_existing=True,
        )
        self.assertEqual(first.id, second.id)
        self.assertEqual(second.text_, "Second version")
        self.assertEqual(second.stt_provider, "cohere")

    def test_manual_transcript_update(self):
        guest_transcript_service.create_guest_transcript(
            self.db, self.guest.id, GuestTranscriptCreate(text="Original with a typo")
        )
        updated = guest_transcript_service.update_guest_transcript_text(
            self.db, self.guest.id, "Corrected text"
        )
        self.assertEqual(updated.text_, "Corrected text")

    def test_manual_update_raises_when_no_transcript_exists(self):
        with self.assertRaises(GuestTranscriptNotFoundError):
            guest_transcript_service.update_guest_transcript_text(
                self.db, self.guest.id, "Some text"
            )

if __name__ == "__main__":
    unittest.main()
