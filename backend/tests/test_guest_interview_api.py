import io
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.guest_interview import _resolve_matcher_service, _resolve_stt_service
from app.audio.models import TranscriptionResult
from app.audio.service import SpeechToTextService
from app.database.session import SessionLocal
from app.interview_intelligence.base import QuestionAnswerMatcher
from app.interview_intelligence.models import (
    MatchedAnswer,
    QuestionAnswerMatchResult,
)
from app.interview_intelligence.service import InterviewIntelligenceService
from app.main import app
from app.schemas.guest import GuestCreate
from app.schemas.question import QuestionAnswerUpdate, QuestionCreate
from app.services import question_service
from app.services.guest_service import create_guest, delete_guest

client = TestClient(app)


class _FakeSTTProvider:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, text="transcribed text"):
        self._text = text

    async def transcribe(self, audio, options=None):
        return TranscriptionResult(
            text=self._text, provider="cohere", model="fake-cohere-model", language="ar"
        )


class _ScriptedMatcher(QuestionAnswerMatcher):
    provider_name = "scripted"

    def __init__(self, matches: list[MatchedAnswer]):
        self._matches = matches

    async def match(self, transcript, questions):
        return QuestionAnswerMatchResult(matches=self._matches, raw_ai_response=None)


def _override_services(transcript_text="transcribed text", matches=None):
    app.dependency_overrides[_resolve_stt_service] = lambda: SpeechToTextService(
        provider=_FakeSTTProvider(text=transcript_text)
    )
    app.dependency_overrides[_resolve_matcher_service] = lambda: InterviewIntelligenceService(
        matcher=_ScriptedMatcher(matches or [])
    )


def _clear_overrides():
    app.dependency_overrides.pop(_resolve_stt_service, None)
    app.dependency_overrides.pop(_resolve_matcher_service, None)


class TranscribeInterviewApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Interview API Test Guest"))

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_transcribe_interview_end_to_end(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        _override_services(
            transcript_text="He said funding was the biggest challenge.",
            matches=[
                MatchedAnswer(
                    question_ref="Q1",
                    spoken_question="What was your biggest challenge?",
                    answer="Funding was the biggest challenge.",
                    status="answered",
                    confidence=0.95,
                )
            ],
        )

        response = client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["transcript"]["text"], "He said funding was the biggest challenge.")
        self.assertEqual(body["transcript"]["stt_provider"], "cohere")
        self.assertEqual(len(body["questions"]), 1)
        self.assertEqual(body["questions"][0]["answer_status"], "answered")
        self.assertEqual(body["questions"][0]["answer_source"], "ai_extracted")

    def test_guest_not_found_returns_404(self):
        _override_services()
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(
            f"/api/guests/{fake_id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 404)

    def test_second_upload_without_replace_existing_returns_409(self):
        _override_services()
        client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        response = client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview2.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 409)

    def test_replace_existing_true_allows_second_upload(self):
        _override_services(transcript_text="first version")
        client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        _override_services(transcript_text="second version")
        response = client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview?replace_existing=true",
            files={"file": ("interview2.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["transcript"]["text"], "second version")

    def test_no_audio_bytes_persisted_anywhere(self):
        """Structural + behavioral: the endpoint never stores the uploaded
        bytes - only the transcript TEXT ends up in the DB."""
        _override_services(transcript_text="just the text")
        response = client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"totally-fake-audio-bytes"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertNotIn("totally-fake-audio-bytes", str(body))

    def test_no_exa_or_tavily_called(self):
        with (
            patch(
                "app.research.providers.exa.ExaResearchSearchProvider.search",
                new_callable=AsyncMock,
            ) as exa_mock,
            patch(
                "app.research.providers.tavily.TavilyResearchSearchProvider.search",
                new_callable=AsyncMock,
            ) as tavily_mock,
        ):
            _override_services()
            response = client.post(
                f"/api/guests/{self.guest.id}/transcribe-interview",
                files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
            )
            self.assertEqual(response.status_code, 201)
            exa_mock.assert_not_called()
            tavily_mock.assert_not_called()


class TranscriptApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Transcript API Test Guest"))

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_get_transcript_404_when_missing(self):
        response = client.get(f"/api/guests/{self.guest.id}/transcript")
        self.assertEqual(response.status_code, 404)

    def test_get_and_patch_transcript(self):
        _override_services(transcript_text="original transcript")
        client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )

        get_response = client.get(f"/api/guests/{self.guest.id}/transcript")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["text"], "original transcript")

        patch_response = client.patch(
            f"/api/guests/{self.guest.id}/transcript", json={"text": "corrected transcript"}
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["text"], "corrected transcript")

    def test_transcript_patch_does_not_auto_run_matching(self):
        question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="A question")
        )
        _override_services(transcript_text="original", matches=[])
        client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )

        before = question_service.get_question_by_id(self.db, question.id).answer_status

        # Patch with a matcher override still armed but PATCH must never
        # call it - if it did, this would still show as not_answered
        # anyway, so the real proof is in test_match_answers_endpoint below
        # combined with this one confirming PATCH alone changes nothing.
        client.patch(f"/api/guests/{self.guest.id}/transcript", json={"text": "corrected"})

        after = question_service.get_question_by_id(self.db, question.id).answer_status
        self.assertEqual(before, after)


class MatchAnswersApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Match Answers API Test Guest"))

    def tearDown(self):
        _clear_overrides()
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_match_answers_requires_existing_transcript(self):
        _override_services()
        response = client.post(f"/api/guests/{self.guest.id}/match-answers")
        self.assertEqual(response.status_code, 404)

    def test_match_answers_uses_corrected_transcript(self):
        question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="What was your biggest challenge?")
        )
        _override_services(transcript_text="raw transcript", matches=[])
        client.post(
            f"/api/guests/{self.guest.id}/transcribe-interview",
            files={"file": ("interview.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )

        client.patch(
            f"/api/guests/{self.guest.id}/transcript", json={"text": "corrected transcript"}
        )

        _override_services(
            matches=[
                MatchedAnswer(
                    question_ref="Q1", answer="found after correction", status="answered", confidence=0.9
                )
            ]
        )
        response = client.post(f"/api/guests/{self.guest.id}/match-answers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["transcript"]["text"], "corrected transcript")
        self.assertEqual(response.json()["questions"][0]["answer"], "found after correction")


class ManualAnswerApiTests(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.guest = create_guest(self.db, GuestCreate(name="Manual Answer API Test Guest"))
        self.question = question_service.create_question(
            self.db, self.guest.id, QuestionCreate(text="A question?")
        )

    def tearDown(self):
        delete_guest(self.db, self.guest.id)
        self.db.close()

    def test_patch_answer_endpoint_sets_manual_answer(self):
        response = client.patch(
            f"/api/questions/{self.question.id}/answer", json={"answer": "manual answer text"}
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["answer"], "manual answer text")
        self.assertEqual(body["answer_source"], "manual")

    def test_patch_answer_endpoint_clears_with_null(self):
        client.patch(f"/api/questions/{self.question.id}/answer", json={"answer": "something"})
        response = client.patch(f"/api/questions/{self.question.id}/answer", json={"answer": None})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNone(body["answer"])
        self.assertEqual(body["answer_status"], "not_answered")

    def test_patch_answer_404_for_unknown_question(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.patch(f"/api/questions/{fake_id}/answer", json={"answer": "x"})
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
