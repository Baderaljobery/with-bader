import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.models.guest import Guest
from app.questions.generation.base import (
    QuestionGenerationError,
    QuestionGenerator,
    QuestionGeneratorTimeoutError,
    QuestionGeneratorValidationError,
)
from app.questions.generation.groq_models import (
    GROQ_QUESTION_GENERATION_JSON_SCHEMA,
    GroqQuestionGenerationSchema,
)
from app.questions.generation.models import (
    QuestionGenerationOptions,
    QuestionGenerationResult,
    ResearchContextItem,
)
from app.questions.generation.postprocess import build_generated_questions
from app.questions.generation.prompts import SYSTEM_PROMPT, build_user_prompt


class GroqQuestionGenerator(QuestionGenerator):
    """Source-grounded interview-question generation via Groq.

    Consumes ONLY the guest metadata and the compact research context the
    caller supplies - no tools, no browsing, no Groq Compound, no built-in
    web search, no Exa/Tavily calls. Research is already complete before
    this class is ever invoked; it only turns already-extracted structured
    research into grounded, structured interview questions.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 1800,
        temperature: float = 0.5,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature

    async def generate(
        self,
        guest: Guest,
        research_items: list[ResearchContextItem],
        options: QuestionGenerationOptions,
    ) -> QuestionGenerationResult:
        indexed = {item.id: item for item in research_items}
        user_prompt = build_user_prompt(guest, research_items, options)

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
                        "name": "guest_question_generation",
                        "schema": GROQ_QUESTION_GENERATION_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                temperature=self._temperature,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise QuestionGeneratorTimeoutError("Groq question generation timed out") from exc
        except APIConnectionError as exc:
            raise QuestionGenerationError(
                f"Groq question generation request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise QuestionGenerationError(
                f"Groq question generation failed with status {status_code}"
            ) from exc

        # Only the final answer channel is ever read - message.reasoning
        # (gpt-oss chain-of-thought, only populated when reasoning_format=
        # "parsed" is explicitly requested, which we never do) is never
        # touched, so no hidden reasoning can end up returned.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise QuestionGeneratorValidationError(
                "Groq returned an empty question generation response"
            )

        try:
            parsed = json.loads(raw_content)
            schema_result = GroqQuestionGenerationSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise QuestionGeneratorValidationError(
                "Groq question generation response failed schema validation"
            ) from exc

        questions = build_generated_questions(schema_result, indexed)

        debug: dict = {
            "provider": "groq",
            "model": self._model,
            "structured_output": schema_result.model_dump(),
        }
        usage = getattr(response, "usage", None)
        if usage is not None:
            debug["input_tokens"] = getattr(usage, "prompt_tokens", None)
            debug["output_tokens"] = getattr(usage, "completion_tokens", None)

        return QuestionGenerationResult(questions=questions, raw_ai_response=debug)
