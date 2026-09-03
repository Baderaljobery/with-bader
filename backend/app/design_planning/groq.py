import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.design_planning.base import (
    SlidePlanner,
    SlidePlanningError,
    SlidePlannerTimeoutError,
    SlidePlannerValidationError,
)
from app.design_planning.groq_models import GROQ_SLIDE_PLAN_JSON_SCHEMA, GroqSlidePlanSchema
from app.design_planning.models import (
    PlanContextItem,
    PlannedSlideResult,
    SlidePlanGenerationResult,
    SlidePlanningOptions,
)
from app.design_planning.prompts import SYSTEM_PROMPT, build_user_prompt
from app.models.guest import Guest


class GroqSlidePlanner(SlidePlanner):
    """Source-grounded, structured multi-slide design-copy planning via
    Groq. Consumes ONLY the guest metadata and the already-selected
    context the caller supplies - no tools, no browsing, no web search.
    Never touches the image-generation provider (OpenRouter/Gemini) - text
    planning and visual generation are fully separate AI capabilities.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 2000,
        temperature: float = 0.6,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature

    async def plan(
        self,
        guest: Guest,
        context_items: list[PlanContextItem],
        options: SlidePlanningOptions,
    ) -> SlidePlanGenerationResult:
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
                        "name": "design_slide_plan",
                        "schema": GROQ_SLIDE_PLAN_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                temperature=self._temperature,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise SlidePlannerTimeoutError("Groq slide planning timed out") from exc
        except APIConnectionError as exc:
            raise SlidePlanningError(f"Groq slide planning request failed: {exc.__class__.__name__}") from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise SlidePlanningError(f"Groq slide planning failed with status {status_code}") from exc

        # Only the final answer channel is ever read - message.reasoning is
        # never touched, so no hidden reasoning can end up returned.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise SlidePlannerValidationError("Groq returned an empty slide planning response")

        try:
            parsed = json.loads(raw_content)
            schema_result = GroqSlidePlanSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise SlidePlannerValidationError("Groq slide planning response failed schema validation") from exc

        if len(schema_result.slides) != len(options.slide_roles):
            raise SlidePlannerValidationError(
                f"Groq returned {len(schema_result.slides)} slide(s), expected "
                f"{len(options.slide_roles)}"
            )

        # Zip positionally against the exact requested (index, role) order -
        # never trust a model-echoed index/role (see groq_models.py).
        slides = [
            PlannedSlideResult(
                index=spec.index,
                role=spec.role,
                headline=raw_slide.headline.strip(),
                body_text=raw_slide.body_text.strip(),
                cta_text=(raw_slide.cta_text.strip() if raw_slide.cta_text else None) or None,
            )
            for spec, raw_slide in zip(options.slide_roles, schema_result.slides, strict=True)
        ]

        if any(not slide.headline for slide in slides):
            raise SlidePlannerValidationError("Groq returned a slide with an empty headline")

        return SlidePlanGenerationResult(slides=slides)
