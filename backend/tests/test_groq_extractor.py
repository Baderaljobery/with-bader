import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APIConnectionError, APIStatusError, APITimeoutError

from app.research.extraction.base import (
    ResearchExtractorConfigurationError,
    ResearchExtractorTimeoutError,
    ResearchExtractorValidationError,
)
from app.research.extraction.groq import GroqResearchExtractor
from app.research.extraction.groq_models import GroqExtractionSchema
from app.research.models import NormalizedResearchSource


class _FakeGuest:
    def __init__(self, name="Test Guest", job_title="CEO", company="Example Co"):
        self.name = name
        self.job_title = job_title
        self.company = company


def _make_response(payload: dict, usage: bool = True):
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    if usage:
        response.usage = MagicMock(prompt_tokens=123, completion_tokens=45)
    else:
        response.usage = None
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return patch(
        "app.research.extraction.groq.AsyncGroq",
        return_value=MagicMock(
            chat=MagicMock(completions=MagicMock(create=mock_create))
        ),
    ), mock_create


_VALID_PAYLOAD = {
    "role_title": "CEO",
    "company": "Example Co",
    "career_history": [],
    "education": [],
    "achievements": [
        {
            "title": "Founded the company",
            "description": None,
            "date": None,
            "source_ids": ["S1"],
            "confidence": 0.8,
        }
    ],
    "projects": [],
    "topics": ["leadership"],
    "interesting_events": [],
    "potential_interview_angles": [],
}


class GroqExtractorTests(unittest.IsolatedAsyncioTestCase):
    def _sources(self):
        return [
            NormalizedResearchSource(
                source_type="website",
                url="https://example.org/a",
                canonical_url="https://example.org/a",
                title="A source",
                content="Some evidence text.",
            )
        ]

    async def test_successful_structured_output_maps_correctly(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await extractor.extract(_FakeGuest(), self._sources())

        self.assertEqual(result.role_title, "CEO")
        self.assertEqual(result.company, "Example Co")
        self.assertEqual(len(result.achievements), 1)
        self.assertEqual(result.achievements[0]["source_urls"], ["https://example.org/a"])
        self.assertEqual(result.raw_ai_response["provider"], "groq")
        self.assertEqual(result.raw_ai_response["model"], "openai/gpt-oss-20b")
        self.assertIn("structured_output", result.raw_ai_response)
        self.assertEqual(result.raw_ai_response["input_tokens"], 123)
        self.assertEqual(result.raw_ai_response["output_tokens"], 45)
        # No reasoning/chain-of-thought field should ever be captured.
        self.assertNotIn("reasoning", result.raw_ai_response)

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            await extractor.extract(_FakeGuest(), self._sources())

        _, kwargs = mock_create.call_args
        for forbidden in ("tools", "tool_choice", "compound_custom", "search_settings", "documents"):
            self.assertNotIn(forbidden, kwargs)

    async def test_invalid_json_raises_validation_error(self):
        response = _make_response({})
        response.choices[0].message.content = "not valid json {"
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractorValidationError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_schema_violating_json_raises_validation_error(self):
        response = _make_response({"achievements": "not a list"})
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractorValidationError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_empty_content_raises_validation_error(self):
        response = _make_response(_VALID_PAYLOAD)
        response.choices[0].message.content = None
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractorValidationError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_timeout_raises_extractor_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractorTimeoutError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_api_error_raises_extraction_error(self):
        from app.research.extraction.base import ResearchExtractionError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        response = httpx.Response(status_code=500, request=request)
        error = APIStatusError("server error", response=response, body={"error": "boom"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractionError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_connection_error_raises_extraction_error(self):
        from app.research.extraction.base import ResearchExtractionError

        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APIConnectionError(request=request))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ResearchExtractionError):
                await extractor.extract(_FakeGuest(), self._sources())

    async def test_arabic_source_text_does_not_crash(self):
        arabic_source = NormalizedResearchSource(
            source_type="website",
            url="https://example.org/ar",
            canonical_url="https://example.org/ar",
            title="مصدر عربي",
            content="سام ألتمان هو الرئيس التنفيذي لشركة أوبن إيه آي.",
        )
        patcher, _ = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await extractor.extract(_FakeGuest(), [arabic_source])
        self.assertEqual(result.role_title, "CEO")

    async def test_empty_source_set_handled(self):
        patcher, mock_create = _patch_create(
            return_value=_make_response(
                {**_VALID_PAYLOAD, "achievements": []}
            )
        )
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await extractor.extract(_FakeGuest(), [])
        self.assertEqual(result.achievements, [])
        _, kwargs = mock_create.call_args
        user_message = kwargs["messages"][1]["content"]
        self.assertIn("no sources were supplied", user_message)

    async def test_guest_only_role_and_company_fallback(self):
        payload = {**_VALID_PAYLOAD, "role_title": None, "company": None, "achievements": []}
        patcher, _ = _patch_create(return_value=_make_response(payload))
        with patcher:
            extractor = GroqResearchExtractor(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await extractor.extract(
                _FakeGuest(job_title="Founder", company="Startup Inc"), self._sources()
            )
        self.assertEqual(result.role_title, "Founder")
        self.assertEqual(result.company, "Startup Inc")


class ExtractorFactoryGroqTests(unittest.TestCase):
    def test_factory_resolves_groq(self):
        from app.core.config import settings
        from app.research.extraction.factory import build_research_extractor

        original_provider = settings.research_extractor_provider
        original_key = settings.groq_api_key
        settings.research_extractor_provider = "groq"
        settings.groq_api_key = "fake-key"
        try:
            extractor = build_research_extractor()
            self.assertIsInstance(extractor, GroqResearchExtractor)
        finally:
            settings.research_extractor_provider = original_provider
            settings.groq_api_key = original_key

    def test_missing_groq_key_fails_clearly(self):
        from app.core.config import settings
        from app.research.extraction.factory import build_research_extractor

        original_provider = settings.research_extractor_provider
        original_key = settings.groq_api_key
        settings.research_extractor_provider = "groq"
        settings.groq_api_key = None
        try:
            with self.assertRaises(ResearchExtractorConfigurationError):
                build_research_extractor()
        finally:
            settings.research_extractor_provider = original_provider
            settings.groq_api_key = original_key


if __name__ == "__main__":
    unittest.main()
