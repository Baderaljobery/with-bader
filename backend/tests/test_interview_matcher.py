import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError

from app.interview_intelligence.base import (
    InterviewMatcherConfigurationError,
    InterviewMatcherTimeoutError,
    InterviewMatcherValidationError,
)
from app.interview_intelligence.groq import GroqQuestionAnswerMatcher
from app.interview_intelligence.mock import MockQuestionAnswerMatcher
from app.interview_intelligence.models import QuestionContext


def _questions() -> list[QuestionContext]:
    return [
        QuestionContext(ref="Q1", question_id="00000000-0000-0000-0000-000000000001", text="What was your biggest challenge?"),
        QuestionContext(ref="Q2", question_id="00000000-0000-0000-0000-000000000002", text="How did you start the company?"),
    ]


def _make_response(payload: dict):
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    response.usage = MagicMock(prompt_tokens=300, completion_tokens=100)
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return patch(
        "app.interview_intelligence.groq.AsyncGroq",
        return_value=MagicMock(chat=MagicMock(completions=MagicMock(create=mock_create))),
    ), mock_create


_VALID_PAYLOAD = {
    "matches": [
        {
            "question_ref": "Q1",
            "spoken_question": "طيب وش أصعب شي مرّيت فيه؟",
            "answer": "والله كانت مشكلة التمويل في البداية.",
            "status": "answered",
            "confidence": 0.92,
        }
    ]
}


class GroqQuestionAnswerMatcherTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_structured_output_maps_correctly(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await matcher.match("some transcript text", _questions())

        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].question_ref, "Q1")
        self.assertEqual(result.matches[0].status, "answered")
        self.assertEqual(result.raw_ai_response["provider"], "groq")
        self.assertNotIn("reasoning", result.raw_ai_response)

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            await matcher.match("transcript", _questions())

        _, kwargs = mock_create.call_args
        for forbidden in (
            "tools",
            "tool_choice",
            "compound_custom",
            "search_settings",
            "documents",
        ):
            self.assertNotIn(forbidden, kwargs)

    async def test_invalid_question_ref_removed(self):
        payload = {
            "matches": [
                {"question_ref": "Q999", "answer": "fabricated", "status": "answered", "confidence": 0.9}
            ]
        }
        patcher, _ = _patch_create(return_value=_make_response(payload))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await matcher.match("transcript", _questions())
        self.assertEqual(result.matches, [])

    async def test_duplicate_match_for_same_question_cleaned(self):
        payload = {
            "matches": [
                {"question_ref": "Q1", "answer": "weak", "status": "uncertain", "confidence": 0.3},
                {"question_ref": "Q1", "answer": "strong confident answer", "status": "answered", "confidence": 0.95},
            ]
        }
        patcher, _ = _patch_create(return_value=_make_response(payload))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await matcher.match("transcript", _questions())
        self.assertEqual(len(result.matches), 1)
        self.assertEqual(result.matches[0].answer, "strong confident answer")

    async def test_invalid_json_raises_validation_error(self):
        response = _make_response({})
        response.choices[0].message.content = "not valid json {"
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(InterviewMatcherValidationError):
                await matcher.match("transcript", _questions())

    async def test_timeout_raises_matcher_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(InterviewMatcherTimeoutError):
                await matcher.match("transcript", _questions())

    async def test_api_error_raises_matching_error(self):
        from app.interview_intelligence.base import InterviewMatchingError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        response = httpx.Response(status_code=500, request=request)
        error = APIStatusError("server error", response=response, body={"error": "boom"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(InterviewMatchingError):
                await matcher.match("transcript", _questions())

    async def test_connection_error_raises_matching_error(self):
        from app.interview_intelligence.base import InterviewMatchingError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APIConnectionError(request=request))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(InterviewMatchingError):
                await matcher.match("transcript", _questions())

    async def test_not_answered_status_preserved(self):
        payload = {"matches": [{"question_ref": "Q2", "answer": None, "status": "not_answered"}]}
        patcher, _ = _patch_create(return_value=_make_response(payload))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await matcher.match("transcript", _questions())
        self.assertEqual(result.matches[0].status, "not_answered")
        self.assertIsNone(result.matches[0].answer)

    async def test_empty_questions_handled(self):
        patcher, mock_create = _patch_create(return_value=_make_response({"matches": []}))
        with patcher:
            matcher = GroqQuestionAnswerMatcher(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await matcher.match("transcript", [])
        self.assertEqual(result.matches, [])
        _, kwargs = mock_create.call_args
        self.assertIn("no saved questions were supplied", kwargs["messages"][1]["content"])


class MockQuestionAnswerMatcherTests(unittest.IsolatedAsyncioTestCase):
    async def test_matches_only_when_question_text_appears_in_transcript(self):
        matcher = MockQuestionAnswerMatcher()
        questions = [
            QuestionContext(ref="Q1", question_id="1", text="biggest challenge"),
            QuestionContext(ref="Q2", question_id="2", text="not mentioned at all"),
        ]
        result = await matcher.match(
            "he talked about his biggest challenge in detail", questions
        )
        refs = {m.question_ref for m in result.matches}
        self.assertEqual(refs, {"Q1"})

    async def test_never_invents_beyond_transcript(self):
        matcher = MockQuestionAnswerMatcher()
        questions = [QuestionContext(ref="Q1", question_id="1", text="hello")]
        result = await matcher.match("hello there", questions)
        self.assertEqual(result.matches[0].answer, "hello there")


class InterviewMatcherFactoryTests(unittest.TestCase):
    def test_factory_resolves_mock(self):
        from app.core.config import settings
        from app.interview_intelligence.factory import build_question_answer_matcher

        original = settings.interview_matcher_provider
        settings.interview_matcher_provider = "mock"
        try:
            matcher = build_question_answer_matcher()
            self.assertIsInstance(matcher, MockQuestionAnswerMatcher)
        finally:
            settings.interview_matcher_provider = original

    def test_factory_resolves_groq(self):
        from app.core.config import settings
        from app.interview_intelligence.factory import build_question_answer_matcher

        original_provider = settings.interview_matcher_provider
        original_key = settings.groq_api_key
        settings.interview_matcher_provider = "groq"
        settings.groq_api_key = "fake-key"
        try:
            matcher = build_question_answer_matcher()
            self.assertIsInstance(matcher, GroqQuestionAnswerMatcher)
        finally:
            settings.interview_matcher_provider = original_provider
            settings.groq_api_key = original_key

    def test_missing_groq_key_fails_clearly(self):
        from app.core.config import settings
        from app.interview_intelligence.factory import build_question_answer_matcher

        original_provider = settings.interview_matcher_provider
        original_key = settings.groq_api_key
        settings.interview_matcher_provider = "groq"
        settings.groq_api_key = None
        try:
            with self.assertRaises(InterviewMatcherConfigurationError):
                build_question_answer_matcher()
        finally:
            settings.interview_matcher_provider = original_provider
            settings.groq_api_key = original_key


if __name__ == "__main__":
    unittest.main()
