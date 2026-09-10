import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError

from app.questions.generation.base import (
    QuestionGeneratorConfigurationError,
    QuestionGeneratorTimeoutError,
    QuestionGeneratorValidationError,
)
from app.questions.generation.groq import GroqQuestionGenerator
from app.questions.generation.mock import MockQuestionGenerator
from app.questions.generation.models import (
    ExistingQuestionItem,
    GeneratedQuestionItem,
    QuestionGenerationOptions,
    ResearchContextItem,
    SemanticComparisonPair,
)


class _FakeGuest:
    def __init__(self, name="Test Guest", job_title="CEO", company="Example Co"):
        self.name = name
        self.job_title = job_title
        self.company = company


def _options(**overrides) -> QuestionGenerationOptions:
    defaults = dict(count=5, language="ar", style="conversational", include_followups=True)
    defaults.update(overrides)
    return QuestionGenerationOptions(**defaults)


def _research_items() -> list[ResearchContextItem]:
    return [
        ResearchContextItem(
            id="R1",
            item_type="career_history",
            fact="Role: CEO | Company: Example Co",
            source_urls=["https://example.org/a"],
        )
    ]


def _make_response(payload: dict, usage: bool = True):
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    response.usage = MagicMock(prompt_tokens=200, completion_tokens=80) if usage else None
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return patch(
        "app.questions.generation.groq.AsyncGroq",
        return_value=MagicMock(chat=MagicMock(completions=MagicMock(create=mock_create))),
    ), mock_create


_VALID_PAYLOAD = {
    "questions": [
        {
            "text": "ما الذي تغيّر في أسلوب قيادتك بعد هذا الانتقال؟",
            "topic": "leadership",
            "category": "turning_point",
            "intent_summary": "leadership change after a career transition",
            "priority": "high",
            "research_item_ids": ["R1"],
            "reason": "Grounded in career history",
            "follow_up_questions": ["هل كان هناك موقف محدد؟"],
        }
    ]
}


class GroqQuestionGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_structured_output_maps_correctly(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await generator.generate(_FakeGuest(), _research_items(), _options())

        self.assertEqual(len(result.questions), 1)
        question = result.questions[0]
        self.assertEqual(question.source_urls, ["https://example.org/a"])
        self.assertEqual(
            question.intent_summary, "leadership change after a career transition"
        )
        self.assertEqual(result.raw_ai_response["provider"], "groq")
        self.assertEqual(result.raw_ai_response["model"], "openai/gpt-oss-20b")
        self.assertNotIn("reasoning", result.raw_ai_response)

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            await generator.generate(_FakeGuest(), _research_items(), _options())

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
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionGeneratorValidationError):
                await generator.generate(_FakeGuest(), _research_items(), _options())

    async def test_schema_violating_json_raises_validation_error(self):
        response = _make_response({"questions": "not a list"})
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionGeneratorValidationError):
                await generator.generate(_FakeGuest(), _research_items(), _options())

    async def test_timeout_raises_generator_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionGeneratorTimeoutError):
                await generator.generate(_FakeGuest(), _research_items(), _options())

    async def test_api_error_raises_generation_error(self):
        from app.questions.generation.base import QuestionGenerationError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        response = httpx.Response(status_code=500, request=request)
        error = APIStatusError("server error", response=response, body={"error": "boom"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionGenerationError):
                await generator.generate(_FakeGuest(), _research_items(), _options())

    async def test_connection_error_raises_generation_error(self):
        from app.questions.generation.base import QuestionGenerationError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APIConnectionError(request=request))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(QuestionGenerationError):
                await generator.generate(_FakeGuest(), _research_items(), _options())

    async def test_requested_count_is_passed_through_to_prompt(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            await generator.generate(_FakeGuest(), _research_items(), _options(count=7))

        _, kwargs = mock_create.call_args
        user_message = kwargs["messages"][1]["content"]
        self.assertIn("requested question count: 7", user_message)

    async def test_arabic_language_reflected_in_prompt(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            await generator.generate(
                _FakeGuest(), _research_items(), _options(language="ar")
            )
        _, kwargs = mock_create.call_args
        self.assertIn("Arabic", kwargs["messages"][1]["content"])

    async def test_english_language_reflected_in_prompt(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            await generator.generate(
                _FakeGuest(), _research_items(), _options(language="en")
            )
        _, kwargs = mock_create.call_args
        self.assertIn("English", kwargs["messages"][1]["content"])

    async def test_followups_included_when_requested(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await generator.generate(
                _FakeGuest(), _research_items(), _options(include_followups=True)
            )
        self.assertEqual(len(result.questions[0].follow_up_questions), 1)

    async def test_empty_research_items_handled(self):
        patcher, mock_create = _patch_create(
            return_value=_make_response({"questions": []})
        )
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await generator.generate(_FakeGuest(), [], _options())
        self.assertEqual(result.questions, [])
        _, kwargs = mock_create.call_args
        self.assertIn("no research items are available", kwargs["messages"][1]["content"])

    async def test_existing_manual_and_ai_questions_are_in_prompt(self):
        existing = [
            ExistingQuestionItem(id="Q1", text="Manual covered?", source="manual"),
            ExistingQuestionItem(
                id="Q2",
                text="AI covered?",
                source="ai_generated",
                intent_summary="covered AI angle",
            ),
        ]
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="test-model")
            await generator.generate(
                _FakeGuest(), _research_items(), _options(), existing
            )
        prompt = mock_create.call_args.kwargs["messages"][1]["content"]
        self.assertIn("Manual covered?", prompt)
        self.assertIn("AI covered?", prompt)
        self.assertIn("covered_intent=covered AI angle", prompt)

    async def test_semantic_pairs_are_classified_in_one_bounded_call(self):
        payload = {
            "decisions": [
                {
                    "pair_id": "P1",
                    "classification": "SAME_TOPIC_DIFFERENT_ANGLE",
                },
                {"pair_id": "P2", "classification": "DUPLICATE"},
            ]
        }
        pairs = [
            SemanticComparisonPair(
                id=f"P{index}",
                candidate=GeneratedQuestionItem(
                    text=f"Candidate {index}?",
                    topic="research",
                    category="research",
                    intent_summary=f"candidate intent {index}",
                ),
                reference=ExistingQuestionItem(
                    id=f"Q{index}",
                    text=f"Reference {index}?",
                    topic="research",
                    intent_summary=f"reference intent {index}",
                ),
            )
            for index in (1, 2)
        ]
        patcher, mock_create = _patch_create(return_value=_make_response(payload))
        with patcher:
            generator = GroqQuestionGenerator(api_key="fake-key", model="test-model")
            decisions = await generator.classify_duplicate_pairs(pairs)
        self.assertEqual(mock_create.await_count, 1)
        self.assertEqual([item.classification for item in decisions], [
            "SAME_TOPIC_DIFFERENT_ANGLE",
            "DUPLICATE",
        ])
        kwargs = mock_create.call_args.kwargs
        self.assertEqual(kwargs["temperature"], 0)
        for forbidden in ("tools", "tool_choice", "search_settings", "documents"):
            self.assertNotIn(forbidden, kwargs)


class MockQuestionGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_generator_respects_requested_count(self):
        generator = MockQuestionGenerator()
        items = [
            ResearchContextItem(id=f"R{i}", item_type="achievement", fact=f"Fact {i}")
            for i in range(1, 10)
        ]
        result = await generator.generate(_FakeGuest(), items, _options(count=3))
        self.assertLessEqual(len(result.questions), 3)

    async def test_mock_generator_never_invents_facts(self):
        generator = MockQuestionGenerator()
        items = [
            ResearchContextItem(
                id="R1", item_type="achievement", fact="Achievement: Founded X", source_urls=["https://a.example"]
            )
        ]
        result = await generator.generate(_FakeGuest(), items, _options())
        for question in result.questions:
            if question.research_item_ids:
                self.assertIn("R1", question.research_item_ids)


class QuestionGeneratorFactoryTests(unittest.TestCase):
    def test_factory_resolves_mock(self):
        from app.core.config import settings
        from app.questions.generation.factory import build_question_generator

        original = settings.question_generator_provider
        settings.question_generator_provider = "mock"
        try:
            generator = build_question_generator()
            self.assertIsInstance(generator, MockQuestionGenerator)
        finally:
            settings.question_generator_provider = original

    def test_factory_resolves_groq(self):
        from app.core.config import settings
        from app.questions.generation.factory import build_question_generator

        original_provider = settings.question_generator_provider
        original_key = settings.groq_api_key
        settings.question_generator_provider = "groq"
        settings.groq_api_key = "fake-key"
        try:
            generator = build_question_generator()
            self.assertIsInstance(generator, GroqQuestionGenerator)
        finally:
            settings.question_generator_provider = original_provider
            settings.groq_api_key = original_key

    def test_missing_groq_key_fails_clearly(self):
        from app.core.config import settings
        from app.questions.generation.factory import build_question_generator

        original_provider = settings.question_generator_provider
        original_key = settings.groq_api_key
        settings.question_generator_provider = "groq"
        settings.groq_api_key = None
        try:
            with self.assertRaises(QuestionGeneratorConfigurationError):
                build_question_generator()
        finally:
            settings.question_generator_provider = original_provider
            settings.groq_api_key = original_key


if __name__ == "__main__":
    unittest.main()
