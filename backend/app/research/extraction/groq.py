import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.models.guest import Guest
from app.research.extraction.base import (
    ResearchExtractionError,
    ResearchExtractor,
    ResearchExtractorTimeoutError,
    ResearchExtractorValidationError,
)
from app.research.extraction.groq_models import GROQ_EXTRACTION_JSON_SCHEMA, GroqExtractionSchema
from app.research.extraction.groq_postprocess import build_extraction_result
from app.research.extraction.prompts import SYSTEM_PROMPT, build_user_prompt
from app.research.extraction.source_selector import (
    assign_source_ids,
    bounded_source_text,
    select_sources_for_extraction,
)
from app.research.models import NormalizedResearchSource, ResearchExtractionResult


class GroqResearchExtractor(ResearchExtractor):
    """Source-grounded structured research extraction via Groq.

    Reasons ONLY over the guest metadata + sources ResearchEngine supplies -
    no tools, no browsing, no Groq Compound, no built-in web search, no
    prior knowledge about the guest. Exa/Tavily remain the only retrieval
    layer; this class only ever turns already-retrieved evidence into
    structured, source-cited output.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 4000,
        reasoning_effort: str = "low",
        max_sources: int | None = None,
        max_source_chars: int | None = None,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._reasoning_effort = reasoning_effort
        self._max_sources = max_sources
        self._max_source_chars = max_source_chars

    async def extract(
        self, guest: Guest, sources: list[NormalizedResearchSource]
    ) -> ResearchExtractionResult:
        selected = select_sources_for_extraction(sources, max_sources=self._max_sources)
        indexed = assign_source_ids(selected)

        source_payload = [
            {
                "id": source_id,
                "title": source.title,
                "publisher": source.publisher,
                "published_at": source.published_at.isoformat() if source.published_at else None,
                "text": bounded_source_text(source, self._max_source_chars),
            }
            for source_id, source in indexed.items()
        ]

        user_prompt = build_user_prompt(guest, source_payload)

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
                        "name": "guest_research_extraction",
                        "schema": GROQ_EXTRACTION_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                reasoning_effort=self._reasoning_effort,
                temperature=0,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise ResearchExtractorTimeoutError("Groq extraction request timed out") from exc
        except APIConnectionError as exc:
            raise ResearchExtractionError(
                f"Groq extraction request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise ResearchExtractionError(
                f"Groq extraction failed with status {status_code}"
            ) from exc

        # Only the final answer channel is ever read - message.reasoning
        # (gpt-oss chain-of-thought, only populated when reasoning_format=
        # "parsed" is explicitly requested, which we never do) is never
        # touched, so no hidden reasoning can end up persisted.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise ResearchExtractorValidationError("Groq returned an empty extraction response")

        try:
            parsed = json.loads(raw_content)
            schema_result = GroqExtractionSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise ResearchExtractorValidationError(
                "Groq extraction response failed schema validation"
            ) from exc

        result = build_extraction_result(schema_result, indexed, guest)

        debug: dict = {
            "provider": "groq",
            "model": self._model,
            "structured_output": schema_result.model_dump(),
        }
        usage = getattr(response, "usage", None)
        if usage is not None:
            debug["input_tokens"] = getattr(usage, "prompt_tokens", None)
            debug["output_tokens"] = getattr(usage, "completion_tokens", None)
        result.raw_ai_response = debug

        return result
