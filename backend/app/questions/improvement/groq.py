import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq
from pydantic import BaseModel, ConfigDict, Field

from app.core.json_schema import build_strict_json_schema
from app.models.question import Question
from app.questions.improvement.base import (
    QuestionImprovementError,
    QuestionImprover,
    QuestionImproverTimeoutError,
    QuestionImproverValidationError,
)
from app.questions.improvement.models import (
    QuestionImprovementContext,
    QuestionImprovementOptions,
    QuestionImprovementResult,
)
from app.questions.improvement.prompts import SYSTEM_PROMPT, build_user_prompt


class _GroqImprovementSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    improved_text: str
    reason: str | None = None
    changes: list[str] = Field(default_factory=list)


_GROQ_IMPROVEMENT_JSON_SCHEMA = build_strict_json_schema(_GroqImprovementSchema)


class GroqQuestionImprover(QuestionImprover):
    """Rewrites the wording of ONE existing question via Groq.

    Consumes only the question's own text and (optionally) lightweight
    guest/research context already on file - no tools, no browsing, no
    Groq Compound, no built-in web search, no Exa/Tavily calls.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 800,
        temperature: float = 0.3,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature

    async def improve(
        self,
        question: Question,
        options: QuestionImprovementOptions,
        context: QuestionImprovementContext | None = None,
    ) -> QuestionImprovementResult:
        original_text = question.text_.strip()
        user_prompt = build_user_prompt(original_text, options, context)

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
                        "name": "question_improvement",
                        "schema": _GROQ_IMPROVEMENT_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                temperature=self._temperature,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise QuestionImproverTimeoutError("Groq question improvement timed out") from exc
        except APIConnectionError as exc:
            raise QuestionImprovementError(
                f"Groq question improvement request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise QuestionImprovementError(
                f"Groq question improvement failed with status {status_code}"
            ) from exc

        # Only the final answer channel is ever read - message.reasoning
        # (only populated when reasoning_format="parsed" is explicitly
        # requested, which we never do) is never touched.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise QuestionImproverValidationError(
                "Groq returned an empty question improvement response"
            )

        try:
            parsed = json.loads(raw_content)
            schema_result = _GroqImprovementSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise QuestionImproverValidationError(
                "Groq question improvement response failed schema validation"
            ) from exc

        improved_text = schema_result.improved_text.strip()
        if not improved_text:
            raise QuestionImproverValidationError("Groq returned an empty improved_text")

        return QuestionImprovementResult(
            original_text=original_text,
            improved_text=improved_text,
            reason=schema_result.reason,
            changes=list(schema_result.changes),
        )
