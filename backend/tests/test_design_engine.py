import unittest
from unittest.mock import AsyncMock, MagicMock

from app.design_generation.base import ImageGenerator
from app.design_generation.engine import (
    SlideImageGenerationEngine,
    SlideImageGenerationError,
    SlideImageRequest,
)
from app.design_generation.models import ImageGenerationResult


def _guest(name="Sam Altman", job_title="CEO", company="OpenAI"):
    guest = MagicMock()
    guest.name = name
    guest.job_title = job_title
    guest.company = company
    return guest


class _FakeImageGenerator(ImageGenerator):
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self):
        self.generate = AsyncMock(
            return_value=ImageGenerationResult(image_bytes=b"fake-bytes", mime_type="image/png")
        )

    async def generate(self, prompt, options):  # pragma: no cover - replaced in __init__
        raise NotImplementedError


def _request(**overrides):
    defaults = dict(
        guest=_guest(),
        template_id="template-01",
        role="cover",
        headline="عنوان",
        body_text="نص",
        platform="linkedin",
        aspect_ratio="1:1",
        background_color="#FFFFFF",
        accent_color="#1B8FEA",
    )
    defaults.update(overrides)
    return SlideImageRequest(**defaults)


class SlideImageGenerationEngineTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.generator = _FakeImageGenerator()
        self.engine = SlideImageGenerationEngine(generator=self.generator)

    async def test_generate_slide_image_loads_real_reference_and_calls_generator(self):
        result = await self.engine.generate_slide_image(_request())

        self.assertEqual(result.image_bytes, b"fake-bytes")
        self.assertEqual(result.generator_provider, "fake")
        self.generator.generate.assert_called_once()
        prompt_arg, options_arg = self.generator.generate.call_args.args
        self.assertIn("NO TEXT IN THIS IMAGE", prompt_arg)
        self.assertEqual(len(options_arg.reference_images), 1)
        self.assertGreater(len(options_arg.reference_images[0].data), 1000)

    async def test_unknown_template_raises_slide_image_generation_error(self):
        with self.assertRaises(SlideImageGenerationError):
            await self.engine.generate_slide_image(_request(template_id="not-a-real-template"))
        self.generator.generate.assert_not_called()

    async def test_different_roles_produce_different_prompts(self):
        await self.engine.generate_slide_image(_request(role="cover"))
        cover_prompt = self.generator.generate.call_args.args[0]
        self.generator.generate.reset_mock()
        await self.engine.generate_slide_image(_request(role="quick_points"))
        quick_points_prompt = self.generator.generate.call_args.args[0]
        self.assertNotEqual(cover_prompt, quick_points_prompt)

    async def test_custom_instructions_override_reaches_prompt(self):
        await self.engine.generate_slide_image(_request(custom_instructions="استخدم أجواء ليلية"))
        prompt_arg = self.generator.generate.call_args.args[0]
        self.assertIn("استخدم أجواء ليلية", prompt_arg)


if __name__ == "__main__":
    unittest.main()
