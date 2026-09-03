import base64
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.design_generation.base import (
    ImageGenerationError,
    ImageGeneratorTimeoutError,
    ImageGeneratorValidationError,
)
from app.design_generation.models import ReferenceImage, SlideImageOptions
from app.design_generation.openrouter import OpenRouterImageGenerator
from app.design_generation.prompts import build_slide_image_prompt


def _guest(name="Sam Altman", job_title="CEO", company="OpenAI"):
    guest = MagicMock()
    guest.name = name
    guest.job_title = job_title
    guest.company = company
    return guest


def _reference() -> ReferenceImage:
    return ReferenceImage(data=b"fake-reference-bytes", mime_type="image/png")


def _options(**overrides):
    defaults = dict(
        platform="linkedin",
        template_id="template-01",
        role="cover",
        aspect_ratio="1:1",
        background_color="#FFFFFF",
        accent_color="#1B8FEA",
        reference_images=[_reference()],
    )
    defaults.update(overrides)
    return SlideImageOptions(**defaults)


def _data_url(image_bytes: bytes = b"fake-image-bytes", mime_type: str = "image/png") -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _make_response(status_code: int = 200, json_body: dict | None = None):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_body or {}
    return response


def _patch_post(side_effect=None, return_value=None):
    mock_post = AsyncMock(side_effect=side_effect, return_value=return_value)
    mock_client = MagicMock()
    mock_client.post = mock_post
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return (
        patch("app.design_generation.openrouter.httpx.AsyncClient", return_value=mock_client),
        mock_post,
    )


_VALID_BODY = {
    "choices": [{"message": {"images": [{"image_url": {"url": _data_url(b"\x89PNG-fake")}}]}}]
}


class OpenRouterImageGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_generation_returns_decoded_image_bytes(self):
        patcher, _ = _patch_post(return_value=_make_response(200, _VALID_BODY))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            result = await generator.generate("a calm abstract gradient", _options())

        self.assertEqual(result.image_bytes, b"\x89PNG-fake")
        self.assertEqual(result.mime_type, "image/png")
        self.assertEqual(generator.provider_name, "openrouter")

    async def test_sends_reference_image_as_multimodal_content_part(self):
        patcher, mock_post = _patch_post(return_value=_make_response(200, _VALID_BODY))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            await generator.generate("prompt", _options())

        _, kwargs = mock_post.call_args
        content = kwargs["json"]["messages"][0]["content"]
        self.assertIsInstance(content, list)
        self.assertEqual(content[0]["type"], "text")
        image_parts = [part for part in content if part["type"] == "image_url"]
        self.assertEqual(len(image_parts), 1)
        self.assertTrue(image_parts[0]["image_url"]["url"].startswith("data:image/png;base64,"))

    async def test_no_reference_images_sends_text_only_content(self):
        patcher, mock_post = _patch_post(return_value=_make_response(200, _VALID_BODY))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            await generator.generate("prompt", _options(reference_images=[]))

        _, kwargs = mock_post.call_args
        content = kwargs["json"]["messages"][0]["content"]
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["type"], "text")

    async def test_sends_modalities_and_image_config_aspect_ratio(self):
        patcher, mock_post = _patch_post(return_value=_make_response(200, _VALID_BODY))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            await generator.generate("prompt", _options(aspect_ratio="4:5"))

        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["modalities"], ["image", "text"])
        self.assertEqual(kwargs["json"]["image_config"], {"aspect_ratio": "4:5"})

    async def test_no_images_in_response_raises_validation_error(self):
        empty_body = {"choices": [{"message": {}}]}
        patcher, _ = _patch_post(return_value=_make_response(200, empty_body))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            with self.assertRaises(ImageGeneratorValidationError):
                await generator.generate("prompt", _options())

    async def test_http_error_status_maps_to_generation_error(self):
        patcher, _ = _patch_post(return_value=_make_response(429, {"error": {"message": "rate limited"}}))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            with self.assertRaises(ImageGenerationError):
                await generator.generate("prompt", _options())

    async def test_timeout_maps_to_timeout_error(self):
        patcher, _ = _patch_post(side_effect=httpx.TimeoutException("timed out"))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="fake-key", model="google/gemini-3.1-flash-image")
            with self.assertRaises(ImageGeneratorTimeoutError):
                await generator.generate("prompt", _options())

    async def test_never_leaks_api_key_in_result(self):
        patcher, _ = _patch_post(return_value=_make_response(200, _VALID_BODY))
        with patcher:
            generator = OpenRouterImageGenerator(api_key="super-secret-key", model="google/gemini-3.1-flash-image")
            result = await generator.generate("prompt", _options())

        self.assertNotIn(b"super-secret-key", result.image_bytes)


class SlideImagePromptTests(unittest.TestCase):
    """Confirms role/platform/color guidance and the no-text + reference-
    safety rules are present, and that role guidance genuinely varies."""

    def _options(self, **overrides):
        defaults = dict(
            platform="linkedin",
            template_id="template-01",
            role="cover",
            aspect_ratio="1:1",
            background_color="#FFFFFF",
            accent_color="#1B8FEA",
            reference_images=[_reference()],
        )
        defaults.update(overrides)
        return SlideImageOptions(**defaults)

    def test_role_guidance_differs_across_all_six_roles(self):
        prompts = {
            role: build_slide_image_prompt(_guest(), self._options(role=role), "", "", [])
            for role in ("cover", "main_content", "continuation", "quote", "quick_points", "closing")
        }
        self.assertEqual(len(set(prompts.values())), 6)

    def test_no_text_rule_present_and_reinforced_twice(self):
        prompt = build_slide_image_prompt(_guest(), self._options(), "headline", "body", [])
        self.assertIn("NO TEXT IN THIS IMAGE", prompt)
        self.assertIn("Final reminder", prompt)

    def test_reference_safety_rule_present(self):
        prompt = build_slide_image_prompt(_guest(), self._options(), "", "", [])
        self.assertIn("Do NOT reproduce, trace, or closely copy", prompt)
        self.assertIn("logos", prompt)

    def test_custom_instructions_included_when_present(self):
        prompt = build_slide_image_prompt(
            _guest(), self._options(custom_instructions="Use a night-sky motif"), "", "", []
        )
        self.assertIn("Use a night-sky motif", prompt)


if __name__ == "__main__":
    unittest.main()
