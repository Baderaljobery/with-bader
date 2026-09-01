import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError

from app.questions.improvement.base import (
    QuestionImproverConfigurationError,
    QuestionImproverTimeoutError,
    QuestionImproverValidationError,
)
from app.questions.improvement.groq import GroqQuestionImprover
from app.questions.improvement.mock import MockQuestionImprover
from app.questions.improvement.models import QuestionImprovementContext, QuestionImprovementOptions


class _FakeQuestion:
    def __init__(self, text: str, guest_id="00000000-0000-0000-0000-000000000001"):
        self.text_ = text
        self.guest_id = guest_id
        self.source = "manual"


def _options(**overrides) -> QuestionImprovementOptions:
    defaults = dict(language="ar", style="conversational", goal="clarity")
    defaults.update(overrides)
    return QuestionImprovementOptions(**defaults)


def _make_response(payload: dict):
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    response.usage = MagicMock(prompt_tokens=80, completion_tokens=30)
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return patch(
        "app.questions.improvement.groq.AsyncGroq",
        return_value=MagicMock(chat=MagicMock(completions=MagicMock(create=mock_create))),
    ), mock_create


_VALID_PAYLOAD = {
    "improved_text": "وش أكبر تحدٍ واجهك في مسيرتك المهنية، وكيف تعاملت معه؟",
    "reason": "Made the question more open-ended and conversational",
    "changes": ["Added a follow-up clause", "Softened the phrasing"],
}


class GroqQuestionImproverTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_structured_output_maps_correctly(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("وش اكبر تحدي واجهته في حياتك المهنية")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await improver.improve(question, _options())

        self.assertEqual(result.original_text, question.text_)
        self.assertEqual(result.improved_text, _VALID_PAYLOAD["improved_text"])
        self.assertEqual(result.reason, _VALID_PAYLOAD["reason"])
        self.assertEqual(len(result.changes), 2)

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            await improver.improve(question, _options(language="en"))

        _, kwargs = mock_create.call_args
        for forbidden in (
            "tools",
            "tool_choice",
            "compound_custom",
            "search_settings",
            "documents",
        ):
            self.assertNotIn(forbidden, kwargs)

    async def test_invalid_json_raises_validation_error(self):
        response = _make_response({})
        response.choices[0].message.content = "not valid json {"
        patcher, _ = _patch_create(return_value=response)
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionImproverValidationError):
                await improver.improve(question, _options())

    async def test_empty_improved_text_raises_validation_error(self):
        response = _make_response({"improved_text": "   "})
        patcher, _ = _patch_create(return_value=response)
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionImproverValidationError):
                await improver.improve(question, _options())

    async def test_timeout_raises_improver_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionImproverTimeoutError):
                await improver.improve(question, _options())

    async def test_api_error_raises_improvement_error(self):
        from app.questions.improvement.base import QuestionImprovementError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        response = httpx.Response(status_code=500, request=request)
        error = APIStatusError("server error", response=response, body={"error": "boom"})
        patcher, _ = _patch_create(side_effect=error)
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionImprovementError):
                await improver.improve(question, _options())

    async def test_connection_error_raises_improvement_error(self):
        from app.questions.improvement.base import QuestionImprovementError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APIConnectionError(request=request))
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionImprovementError):
                await improver.improve(question, _options())

    async def test_arabic_language_reflected_in_prompt(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("وش اكبر تحدي واجهته")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            await improver.improve(question, _options(language="ar"))
        _, kwargs = mock_create.call_args
        self.assertIn("Arabic", kwargs["messages"][1]["content"])

    async def test_english_language_reflected_in_prompt(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            await improver.improve(question, _options(language="en"))
        _, kwargs = mock_create.call_args
        self.assertIn("English", kwargs["messages"][1]["content"])

    async def test_optional_context_is_labeled_as_not_a_new_fact_source(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("What was your biggest challenge?")
        context = QuestionImprovementContext(
            guest_name="Test Guest", guest_job_title="CEO", guest_company="Example Co"
        )
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            await improver.improve(question, _options(language="en"), context)
        _, kwargs = mock_create.call_args
        user_message = kwargs["messages"][1]["content"]
        self.assertIn("Example Co", user_message)
        self.assertIn("do NOT pull new facts", user_message)

    async def test_none_context_does_not_crash(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        question = _FakeQuestion("What was your biggest challenge?")
        with patcher:
            improver = GroqQuestionImprover(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await improver.improve(question, _options(language="en"), context=None)
        self.assertEqual(result.improved_text, _VALID_PAYLOAD["improved_text"])


class MockQuestionImproverTests(unittest.IsolatedAsyncioTestCase):
    async def test_english_example_matches_expected_style(self):
        improver = MockQuestionImprover()
        question = _FakeQuestion("What was your biggest challenge?")
        result = await improver.improve(question, _options(language="en"))
        self.assertEqual(
            result.improved_text, "What was your biggest challenge, and how did you deal with it?"
        )

    async def test_arabic_output_ends_with_arabic_question_mark(self):
        improver = MockQuestionImprover()
        question = _FakeQuestion("وش اكبر تحدي واجهته في حياتك المهنية")
        result = await improver.improve(question, _options(language="ar"))
        self.assertTrue(result.improved_text.endswith("؟"))

    async def test_never_invents_facts_beyond_original_text(self):
        improver = MockQuestionImprover()
        question = _FakeQuestion("What was your biggest challenge?")
        result = await improver.improve(question, _options(language="en"))
        self.assertIn("What was your biggest challenge", result.improved_text)


class QuestionImproverFactoryTests(unittest.TestCase):
    def test_factory_resolves_mock(self):
        from app.core.config import settings
        from app.questions.improvement.factory import build_question_improver

        original = settings.question_improver_provider
        settings.question_improver_provider = "mock"
        try:
            improver = build_question_improver()
            self.assertIsInstance(improver, MockQuestionImprover)
        finally:
            settings.question_improver_provider = original

    def test_factory_resolves_groq(self):
        from app.core.config import settings
        from app.questions.improvement.factory import build_question_improver

        original_provider = settings.question_improver_provider
        original_key = settings.groq_api_key
        settings.question_improver_provider = "groq"
        settings.groq_api_key = "fake-key"
        try:
            improver = build_question_improver()
            self.assertIsInstance(improver, GroqQuestionImprover)
        finally:
            settings.question_improver_provider = original_provider
            settings.groq_api_key = original_key

    def test_missing_groq_key_fails_clearly(self):
        from app.core.config import settings
        from app.questions.improvement.factory import build_question_improver

        original_provider = settings.question_improver_provider
        original_key = settings.groq_api_key
        settings.question_improver_provider = "groq"
        settings.groq_api_key = None
        try:
            with self.assertRaises(QuestionImproverConfigurationError):
                build_question_improver()
        finally:
            settings.question_improver_provider = original_provider
            settings.groq_api_key = original_key


if __name__ == "__main__":
    unittest.main()
