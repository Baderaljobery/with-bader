import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from groq import APITimeoutError

from app.design_planning.base import SlidePlannerTimeoutError, SlidePlannerValidationError
from app.design_planning.groq import GroqSlidePlanner
from app.design_planning.models import PlanContextItem, SlidePlanningOptions, SlideRoleSpec
from app.design_planning.prompts import build_user_prompt


def _guest(name="Sam Altman", job_title="CEO", company="OpenAI"):
    guest = MagicMock()
    guest.name = name
    guest.job_title = job_title
    guest.company = company
    return guest


def _context_items():
    return [PlanContextItem(id="C1", category="content_draft", text="نص تجريبي عن العودة للقيادة.")]


def _options(**overrides):
    defaults = dict(
        platform="linkedin",
        slide_roles=[SlideRoleSpec(index=1, role="cover"), SlideRoleSpec(index=2, role="main_content")],
        template_id="template-01",
    )
    defaults.update(overrides)
    return SlidePlanningOptions(**defaults)


def _make_response(slides: list[dict]):
    message = MagicMock()
    message.content = json.dumps({"slides": slides})
    choice = MagicMock()
    choice.message = message
    response = MagicMock()
    response.choices = [choice]
    return response


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    return (
        patch(
            "app.design_planning.groq.AsyncGroq",
            return_value=MagicMock(chat=MagicMock(completions=MagicMock(create=mock_create))),
        ),
        mock_create,
    )


_VALID_SLIDES = [
    {"headline": "عنوان الافتتاحية", "body_text": "", "cta_text": None},
    {"headline": "عنوان المحتوى الرئيسي", "body_text": "شرح قصير.", "cta_text": None},
]


class GroqSlidePlannerTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_plan_zips_positionally_against_requested_roles(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_SLIDES))
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            result = await planner.plan(_guest(), _context_items(), _options())

        self.assertEqual(len(result.slides), 2)
        self.assertEqual(result.slides[0].index, 1)
        self.assertEqual(result.slides[0].role, "cover")
        self.assertEqual(result.slides[0].headline, "عنوان الافتتاحية")
        self.assertEqual(result.slides[1].index, 2)
        self.assertEqual(result.slides[1].role, "main_content")

    async def test_call_does_not_enable_tools_or_web_search(self):
        patcher, mock_create = _patch_create(return_value=_make_response(_VALID_SLIDES))
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            await planner.plan(_guest(), _context_items(), _options())

        _, kwargs = mock_create.call_args
        for forbidden in ("tools", "tool_choice", "compound_custom", "search_settings", "documents"):
            self.assertNotIn(forbidden, kwargs)

    async def test_wrong_slide_count_raises_validation_error(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_SLIDES[:1]))
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(SlidePlannerValidationError):
                await planner.plan(_guest(), _context_items(), _options())

    async def test_empty_headline_raises_validation_error(self):
        bad_slides = [{"headline": "", "body_text": "x", "cta_text": None}, _VALID_SLIDES[1]]
        patcher, _ = _patch_create(return_value=_make_response(bad_slides))
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(SlidePlannerValidationError):
                await planner.plan(_guest(), _context_items(), _options())

    async def test_malformed_json_raises_validation_error(self):
        message = MagicMock()
        message.content = "not json"
        choice = MagicMock()
        choice.message = message
        response = MagicMock()
        response.choices = [choice]
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(SlidePlannerValidationError):
                await planner.plan(_guest(), _context_items(), _options())

    async def test_timeout_maps_to_timeout_error(self):
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
        patcher, _ = _patch_create(side_effect=APITimeoutError(request=request))
        with patcher:
            planner = GroqSlidePlanner(api_key="fake-key", model="openai/gpt-oss-20b")
            with self.assertRaises(SlidePlannerTimeoutError):
                await planner.plan(_guest(), _context_items(), _options())

    async def test_never_leaks_api_key_or_reasoning_shape(self):
        patcher, _ = _patch_create(return_value=_make_response(_VALID_SLIDES))
        with patcher:
            planner = GroqSlidePlanner(api_key="super-secret-key", model="openai/gpt-oss-20b")
            result = await planner.plan(_guest(), _context_items(), _options())

        for slide in result.slides:
            self.assertNotIn("super-secret-key", slide.headline)
            self.assertFalse(hasattr(slide, "reasoning"))


class SlidePlanningPromptTests(unittest.TestCase):
    def test_requested_roles_and_order_are_listed(self):
        prompt = build_user_prompt(_guest(), _context_items(), _options())
        self.assertIn("slide 1: role = cover", prompt)
        self.assertIn("slide 2: role = main_content", prompt)

    def test_no_context_items_says_so_explicitly(self):
        prompt = build_user_prompt(_guest(), [], _options())
        self.assertIn("no context items were selected", prompt)

    def test_custom_instructions_included_when_present(self):
        prompt = build_user_prompt(
            _guest(), _context_items(), _options(custom_instructions="ركز على قصة الرجوع")
        )
        self.assertIn("ركز على قصة الرجوع", prompt)


if __name__ == "__main__":
    unittest.main()
