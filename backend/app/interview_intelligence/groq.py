import json

from groq import APIConnectionError, APIError, APITimeoutError, AsyncGroq

from app.interview_intelligence.base import (
    InterviewMatcherTimeoutError,
    InterviewMatcherValidationError,
    InterviewMatchingError,
    QuestionAnswerMatcher,
)
from app.interview_intelligence.groq_models import (
    GROQ_INTERVIEW_MATCH_JSON_SCHEMA,
    GroqInterviewMatchSchema,
)
from app.interview_intelligence.models import QuestionAnswerMatchResult, QuestionContext
from app.interview_intelligence.postprocess import build_matches
from app.interview_intelligence.prompts import SYSTEM_PROMPT, build_user_prompt


class GroqQuestionAnswerMatcher(QuestionAnswerMatcher):
    """Matches interview-transcript content to saved questions via Groq.

    Consumes ONLY the transcript text + saved question list the caller
    supplies - no tools, no browsing, no Groq Compound, no built-in web
    search, no Exa/Tavily calls. This is extraction, not research: the
    transcript is already complete before this class is ever invoked.
    """

    provider_name = "groq"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        max_output_tokens: int = 1800,
        temperature: float = 0.2,
    ) -> None:
        self._client = AsyncGroq(api_key=api_key, timeout=timeout_seconds)
        self._model = model
        self.model_name = model
        self._max_output_tokens = max_output_tokens
        self._temperature = temperature

    async def match(
        self, transcript: str, questions: list[QuestionContext]
    ) -> QuestionAnswerMatchResult:
        valid_refs = {question.ref for question in questions}
        user_prompt = build_user_prompt(transcript, questions)

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
                        "name": "interview_question_answer_match",
                        "schema": GROQ_INTERVIEW_MATCH_JSON_SCHEMA,
                        "strict": True,
                    },
                },
                max_completion_tokens=self._max_output_tokens,
                temperature=self._temperature,
                # Deliberately no tools/tool_choice/compound_custom/search_settings/
                # documents - this call must never browse or search the web itself.
            )
        except APITimeoutError as exc:
            raise InterviewMatcherTimeoutError("Groq interview matching timed out") from exc
        except APIConnectionError as exc:
            raise InterviewMatchingError(
                f"Groq interview matching request failed: {exc.__class__.__name__}"
            ) from exc
        except APIError as exc:
            status_code = getattr(exc, "status_code", "unknown")
            raise InterviewMatchingError(
                f"Groq interview matching failed with status {status_code}"
            ) from exc

        # Only the final answer channel is ever read - message.reasoning
        # (only populated when reasoning_format="parsed" is explicitly
        # requested, which we never do) is never touched.
        raw_content = response.choices[0].message.content if response.choices else None
        if not raw_content:
            raise InterviewMatcherValidationError("Groq returned an empty matching response")

        try:
            parsed = json.loads(raw_content)
            schema_result = GroqInterviewMatchSchema.model_validate(parsed)
        except (json.JSONDecodeError, ValueError) as exc:
            raise InterviewMatcherValidationError(
                "Groq interview matching response failed schema validation"
            ) from exc

        matches = build_matches(schema_result, valid_refs)

        debug: dict = {
            "provider": "groq",
            "model": self._model,
            "structured_output": schema_result.model_dump(),
        }
        usage = getattr(response, "usage", None)
        if usage is not None:
            debug["input_tokens"] = getattr(usage, "prompt_tokens", None)
            debug["output_tokens"] = getattr(usage, "completion_tokens", None)

        return QuestionAnswerMatchResult(matches=matches, raw_ai_response=debug)
