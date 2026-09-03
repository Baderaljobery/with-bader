import base64

import httpx

from app.design_generation.base import (
    ImageGenerationError,
    ImageGenerator,
    ImageGeneratorTimeoutError,
    ImageGeneratorValidationError,
)
from app.design_generation.models import ImageGenerationResult, SlideImageOptions

_OPENROUTER_CHAT_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"


def _reference_data_url(image_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


class OpenRouterImageGenerator(ImageGenerator):
    """The only image-generation provider for this phase. Calls the
    configured image-capable model (default: Google's Gemini 3.1 Flash
    Image) through OpenRouter's OpenAI-compatible /chat/completions
    endpoint, using its "modalities"/"image_config" image-generation
    extension - no Google Cloud billing/quota dependency, unlike calling
    Gemini directly. Consumes a single already-built prompt string plus the
    selected template's real reference image bytes (see templates.py) and
    returns raw generated image bytes - it never renders text itself,
    never persists anything, and never touches the database.
    """

    provider_name = "openrouter"

    def __init__(self, api_key: str, model: str, timeout_seconds: float = 60.0) -> None:
        self._api_key = api_key
        self._model = model
        self.model_name = model
        self._timeout_seconds = timeout_seconds

    async def generate(self, prompt: str, options: SlideImageOptions) -> ImageGenerationResult:
        # OpenAI-compatible multimodal content: the reference image(s) are
        # supplied as real image_url (data-URI) parts, never just described
        # in text - see prompts.py's _REFERENCE_USAGE_RULE for how the
        # model is told to use them (inspiration only, never to copy).
        content: list[dict] = [{"type": "text", "text": prompt}]
        for reference in options.reference_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": _reference_data_url(reference.data, reference.mime_type)},
                }
            )

        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": content}],
            "modalities": ["image", "text"],
            "image_config": {"aspect_ratio": options.aspect_ratio},
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    _OPENROUTER_CHAT_COMPLETIONS_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                        # Optional OpenRouter attribution headers - harmless
                        # to include, help OpenRouter's own model rankings.
                        "HTTP-Referer": "https://withbader.app",
                        "X-Title": "With Bader",
                    },
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise ImageGeneratorTimeoutError("OpenRouter image generation timed out") from exc
        except httpx.TransportError as exc:
            raise ImageGenerationError(
                f"OpenRouter image generation request failed: {exc.__class__.__name__}"
            ) from exc

        if response.status_code >= 400:
            raise ImageGenerationError(
                f"OpenRouter image generation failed with status {response.status_code}"
            )

        try:
            data = response.json()
            choices = data["choices"]
            message = choices[0]["message"]
            images = message.get("images") or []
            image_url = images[0]["image_url"]["url"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ImageGeneratorValidationError(
                "OpenRouter did not return a generated image"
            ) from exc

        if not image_url.startswith("data:"):
            raise ImageGeneratorValidationError("OpenRouter returned an unexpected image format")

        header, _, encoded = image_url.partition(",")
        mime_type = header.removeprefix("data:").split(";")[0] or "image/png"
        try:
            image_bytes = base64.b64decode(encoded)
        except (ValueError, TypeError) as exc:
            raise ImageGeneratorValidationError(
                "OpenRouter returned malformed image data"
            ) from exc

        if not image_bytes:
            raise ImageGeneratorValidationError("OpenRouter returned an empty image")

        return ImageGenerationResult(image_bytes=image_bytes, mime_type=mime_type)
