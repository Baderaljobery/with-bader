import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.content.generation.base import (
    ContentGenerationError,
    ContentGenerator,
    ContentGeneratorTimeoutError,
    ContentGeneratorValidationError,
)
from app.content.generation.groq_models import (
    GROQ_CONTENT_GENERATION_JSON_SCHEMA,
    GroqContentGenerationSchema,
)
from app.content.generation.models import (
    ContentContextItem,
    ContentGenerationOptions,
    ContentGenerationResult,
)
from app.content.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.models.guest import Guest


class GroqContentGenerator(ContentGenerator):
    """Source-grounded social-content generation via Groq.

    Consumes ONLY the guest metadata and the compact context the caller
    supplies - no tools, no browsing, no Groq Compound, no built-in web
    search, no Exa/Tavily calls. Research/interview/notebook work is already
    complete before this class is ever invoked.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 1800,
        temperature: float = 0.7,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature

    async def generate(
        self,
        guest: Guest,
        context_items: list[ContentContextItem],
        options: ContentGenerationOptions,
    ) -> ContentGenerationResult:
        user_prompt = build_user_prompt(guest, context_items, options)

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "guest_content_generation",
                        "schema": GROQ_CONTENT_GENERATION_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                temperature=self._temperature,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise ContentGeneratorTimeoutError("Groq content generation timed out") from exc
        except APIConnectionError as exc:
            raise ContentGenerationError(
                f"Groq content generation request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise ContentGenerationError(
                f"Groq content generation failed with status {status_code}"
            ) from exc

        # Only the final answer channel is ever read - message.reasoning
        # (gpt-oss chain-of-thought) is never touched, so no hidden
        # reasoning can end up returned to the frontend.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise ContentGeneratorValidationError(
                "Groq returned an empty content generation response"
            )

        try:
            parsed = json.loads(raw_content)
            schema_result = GroqContentGenerationSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ContentGeneratorValidationError(
                "Groq content generation response failed schema validation"
            ) from exc

        text = schema_result.content.strip()
        if not text:
            raise ContentGeneratorValidationError("Groq content generation returned empty content")

        title = schema_result.title.strip() if schema_result.title else None
        return ContentGenerationResult(title=title or None, content=text)
