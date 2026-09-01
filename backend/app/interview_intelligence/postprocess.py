from app.interview_intelligence.groq_models import GroqInterviewMatchSchema
from app.interview_intelligence.models import MatchedAnswer


def _richness(match: MatchedAnswer) -> tuple:
    return (
        1 if match.status == "answered" else 0,
        match.confidence or 0.0,
        1 if match.answer else 0,
        len(match.answer or ""),
    )


def _dedupe_by_question_ref(matches: list[MatchedAnswer]) -> list[MatchedAnswer]:
    """AI may accidentally return multiple matches for the same question -
    keep the richer one: answered > higher confidence > non-empty answer >
    longer meaningful answer."""
    best: dict[str, MatchedAnswer] = {}
    order: list[str] = []
    for match in matches:
        existing = best.get(match.question_ref)
        if existing is None:
            order.append(match.question_ref)
            best[match.question_ref] = match
        elif _richness(match) > _richness(existing):
            best[match.question_ref] = match
    return [best[ref] for ref in order]


def build_matches(
    schema_result: GroqInterviewMatchSchema, valid_refs: set[str]
) -> list[MatchedAnswer]:
    """Convert the raw (LLM-produced) schema into trusted matches: any
    question_ref not in valid_refs (Q999, a UUID, an invented ref, ...) is
    dropped entirely rather than trusted."""
    processed: list[MatchedAnswer] = []

    for raw in schema_result.matches:
        if raw.question_ref not in valid_refs:
            continue
        processed.append(
            MatchedAnswer(
                question_ref=raw.question_ref,
                spoken_question=raw.spoken_question,
                answer=raw.answer,
                status=raw.status,
                confidence=raw.confidence,
            )
        )

    return _dedupe_by_question_ref(processed)
