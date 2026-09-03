import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APITimeoutError

from app.content.generation.base import (
    ContentGeneratorTimeoutError,
    ContentGeneratorValidationError,
)
from app.content.generation.groq import GroqContentGenerator
from app.content.generation.models import ContentContextItem, ContentGenerationOptions
from app.content.generation.prompts import build_user_prompt


def _guest(name="Sam Altman", job_title="CEO", company="OpenAI"):
    guest = MagicMock()
    guest.name = name
    guest.job_title = job_title
    guest.company = company
    return guest


def _context_items():
    return [
        ContentContextItem(id="A1", category="answers", text="Q: Biggest risk?\nA: Leaving to return as CEO."),
        ContentContextItem(id="N1", category="notebook", text="[content_idea] the return-to-CEO angle"),
    ]


def _make_response(payload: dict):
    message = MagicMock()
    message.content = json.dumps(payload)
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    response.usage = MagicMock(prompt_tokens=200, completion_tokens=80)
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return (
        patch(
            "app.content.generation.groq.AsyncGroq",
            return_value=MagicMock(chat=MagicMock(completions=MagicMock(create=mock_create))),
        ),
        mock_create,
    )


_VALID_PAYLOAD = {"title": None, "content": "نص تجريبي مبني على البيانات المتاحة فقط."}


class GroqContentGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_structured_output_maps_correctly(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        options = ContentGenerationOptions(platform="linkedin", length="medium", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await generator.generate(_guest(), _context_items(), options)

        self.assertEqual(result.content, _VALID_PAYLOAD["content"])
        self.assertIsNone(result.title)
        self.assertEqual(generator.provider_name, "groq")
        self.assertEqual(generator.model_name, "openai/gpt-oss-20b")

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        options = ContentGenerationOptions(platform="x", length="short", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            await generator.generate(_guest(), _context_items(), options)

        _, kwargs = mock_create.call_args
        for forbidden in ("tools", "tool_choice", "compound_custom", "search_settings", "documents"):
            self.assertNotIn(forbidden, kwargs)

    async def test_empty_content_raises_validation_error(self):
        patcher, _ = _patch_create(return_value=_make_response({"title": None, "content": "   "}))
        options = ContentGenerationOptions(platform="general", length="short", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ContentGeneratorValidationError):
                await generator.generate(_guest(), _context_items(), options)

    async def test_malformed_json_raises_validation_error(self):
        message = MagicMock()
        message.content = "not json"
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]
        patcher, _ = _patch_create(return_value=response)
        options = ContentGenerationOptions(platform="linkedin", length="medium", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ContentGeneratorValidationError):
                await generator.generate(_guest(), _context_items(), options)

    async def test_timeout_maps_to_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        options = ContentGenerationOptions(platform="linkedin", length="medium", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(ContentGeneratorTimeoutError):
                await generator.generate(_guest(), _context_items(), options)

    async def test_never_leaks_api_key_or_raw_response_shape(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_PAYLOAD))
        options = ContentGenerationOptions(platform="linkedin", length="detailed", language="ar")
        with patcher:
            generator = GroqContentGenerator(api_key="super-secret-key", model="openai/gpt-oss-20b")
            result = await generator.generate(_guest(), _context_items(), options)

        # The only thing exposed to callers is title/content - never the
        # API key, raw message object, or reasoning channel.
        self.assertNotIn("super-secret-key", result.content)
        self.assertFalse(hasattr(result, "reasoning"))
        self.assertFalse(hasattr(result, "raw_ai_response"))


class ContentPromptTests(unittest.TestCase):
    """Confirms platform/length guidance actually varies the prompt text -
    not hard-coded character counts, semantic instructions instead."""

    def test_platform_guidance_differs_between_linkedin_and_x(self):
        options_linkedin = ContentGenerationOptions(platform="linkedin", length="medium", language="ar")
        options_x = ContentGenerationOptions(platform="x", length="medium", language="ar")
        prompt_linkedin = build_user_prompt(_guest(), [], options_linkedin)
        prompt_x = build_user_prompt(_guest(), [], options_x)

        self.assertNotEqual(prompt_linkedin, prompt_x)
        self.assertIn("LinkedIn", prompt_linkedin)
        self.assertIn("X (Twitter)", prompt_x)

    def test_length_guidance_differs_between_short_and_detailed(self):
        options_short = ContentGenerationOptions(platform="linkedin", length="short", language="ar")
        options_detailed = ContentGenerationOptions(platform="linkedin", length="detailed", language="ar")
        prompt_short = build_user_prompt(_guest(), [], options_short)
        prompt_detailed = build_user_prompt(_guest(), [], options_detailed)

        self.assertIn("Short:", prompt_short)
        self.assertIn("Detailed:", prompt_detailed)
        self.assertNotEqual(prompt_short, prompt_detailed)

    def test_unanswered_questions_labeled_as_hints_not_facts(self):
        options = ContentGenerationOptions(platform="linkedin", length="medium", language="ar")
        items = [ContentContextItem(id="Q1", category="questions", text="Some question?")]
        prompt = build_user_prompt(_guest(), items, options)
        self.assertIn("topic hints only - NOT answered facts", prompt)

    def test_custom_instructions_included_when_present(self):
        options = ContentGenerationOptions(
            platform="linkedin", length="medium", language="ar", custom_instructions="Mention the podcast launch"
        )
        prompt = build_user_prompt(_guest(), [], options)
        self.assertIn("Mention the podcast launch", prompt)


if __name__ == "__main__":
    unittest.main()
