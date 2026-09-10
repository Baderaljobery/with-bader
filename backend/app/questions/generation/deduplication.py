from collections import OrderedDict, deque
from dataclasses import dataclass

from app.questions.generation.base import QuestionGenerationError, QuestionGenerator
from app.questions.generation.models import (
    ExistingQuestionItem,
    GeneratedQuestionItem,
    SemanticComparisonPair,
)
from app.questions.generation.similarity import (
    lexical_similarity,
    normalize_question_text,
    same_optional_label,
)


@dataclass
class DuplicateFilterResult:
    accepted: list[GeneratedQuestionItem]
    rejected: list[GeneratedQuestionItem]
    semantic_pairs_checked: int = 0


def _as_reference(item: GeneratedQuestionItem) -> ExistingQuestionItem:
    return ExistingQuestionItem(
        id=f"candidate:{item.candidate_id}",
        text=item.text,
        topic=item.topic,
        source="candidate",
        intent_summary=item.intent_summary,
        research_item_ids=item.research_item_ids,
    )


def _is_deterministic_duplicate(
    candidate: GeneratedQuestionItem,
    reference: ExistingQuestionItem,
    lexical_duplicate_threshold: float,
    intent_duplicate_threshold: float,
) -> bool:
    if normalize_question_text(candidate.text) == normalize_question_text(reference.text):
        return True

    text_score = lexical_similarity(candidate.text, reference.text)
    if candidate.intent_summary and reference.intent_summary:
        intent_score = lexical_similarity(candidate.intent_summary, reference.intent_summary)
        if normalize_question_text(candidate.intent_summary) == normalize_question_text(
            reference.intent_summary
        ):
            return True
        if intent_score >= intent_duplicate_threshold and (
            same_optional_label(candidate.topic, reference.topic)
            or text_score >= lexical_duplicate_threshold * 0.65
        ):
            return True
        # A different explicit intent should be left for semantic judgment,
        # even if the two question wordings share most topic words.
        return False
    return text_score >= lexical_duplicate_threshold


def _plausibility_score(
    candidate: GeneratedQuestionItem,
    reference: ExistingQuestionItem,
    semantic_candidate_threshold: float,
) -> float:
    text_score = lexical_similarity(candidate.text, reference.text)
    intent_score = (
        lexical_similarity(candidate.intent_summary, reference.intent_summary)
        if candidate.intent_summary and reference.intent_summary
        else 0.0
    )
    shared_research = bool(
        set(candidate.research_item_ids) & set(reference.research_item_ids)
    )
    same_topic = same_optional_label(candidate.topic, reference.topic)
    if not (
        text_score >= semantic_candidate_threshold
        or intent_score >= semantic_candidate_threshold
        or shared_research
        or same_topic
    ):
        return 0.0
    return max(
        text_score,
        intent_score,
        0.45 if shared_research else 0.0,
        0.25 if same_topic else 0.0,
    )


async def filter_unique_candidates(
    candidates: list[GeneratedQuestionItem],
    existing_questions: list[ExistingQuestionItem],
    generator: QuestionGenerator,
    *,
    lexical_duplicate_threshold: float,
    intent_duplicate_threshold: float,
    semantic_candidate_threshold: float,
    max_semantic_pairs: int,
) -> DuplicateFilterResult:
    """Layered exact, lexical/intent and one-call semantic filtering.

    Semantic comparisons are only prepared for plausible overlaps and are
    globally capped. The provider receives the selected pairs in one batch,
    never one request per pair.
    """
    deterministic_survivors: list[GeneratedQuestionItem] = []
    rejected: list[GeneratedQuestionItem] = []

    for candidate in candidates:
        references = [
            *existing_questions,
            *(_as_reference(item) for item in deterministic_survivors),
        ]
        if any(
            _is_deterministic_duplicate(
                candidate,
                reference,
                lexical_duplicate_threshold,
                intent_duplicate_threshold,
            )
            for reference in references
        ):
            rejected.append(candidate)
        else:
            deterministic_survivors.append(candidate)

    pairs_by_candidate: OrderedDict[
        str, list[tuple[float, SemanticComparisonPair]]
    ] = OrderedDict()
    pair_number = 0
    for candidate_index, candidate in enumerate(deterministic_survivors):
        references = [
            *existing_questions,
            *(
                _as_reference(item)
                for item in deterministic_survivors[:candidate_index]
            ),
        ]
        for reference in references:
            score = _plausibility_score(
                candidate, reference, semantic_candidate_threshold
            )
            if score:
                pair_number += 1
                pair = SemanticComparisonPair(
                    id=f"P{pair_number}",
                    candidate=candidate,
                    reference=reference,
                )
                pairs_by_candidate.setdefault(str(candidate.candidate_id), []).append(
                    (score, pair)
                )

    pair_queues: OrderedDict[str, deque[SemanticComparisonPair]] = OrderedDict()
    for candidate_id, scored in pairs_by_candidate.items():
        scored.sort(key=lambda item: item[0], reverse=True)
        pair_queues[candidate_id] = deque(pair for _, pair in scored)

    # Round-robin the best matches per candidate so a guest with many old
    # questions on one topic cannot consume the entire semantic pair budget.
    pairs: list[SemanticComparisonPair] = []
    while pair_queues and len(pairs) < max_semantic_pairs:
        empty: list[str] = []
        for candidate_id, queue in pair_queues.items():
            if queue and len(pairs) < max_semantic_pairs:
                pairs.append(queue.popleft())
            if not queue:
                empty.append(candidate_id)
        for candidate_id in empty:
            pair_queues.pop(candidate_id, None)
    decisions = []
    if pairs:
        try:
            decisions = await generator.classify_duplicate_pairs(pairs)
        except QuestionGenerationError:
            # Generation remains available if the secondary validator is
            # temporarily unavailable; exact and conservative intent/lexical
            # checks have already run, and the generation prompt also avoids
            # historical questions.
            decisions = []

    duplicate_pair_ids = {
        decision.pair_id
        for decision in decisions
        if decision.classification == "DUPLICATE"
    }
    duplicate_candidate_ids = {
        str(pair.candidate.candidate_id)
        for pair in pairs
        if pair.id in duplicate_pair_ids
    }

    accepted: list[GeneratedQuestionItem] = []
    for candidate in deterministic_survivors:
        if str(candidate.candidate_id) in duplicate_candidate_ids:
            rejected.append(candidate)
        else:
            accepted.append(candidate)

    return DuplicateFilterResult(
        accepted=accepted,
        rejected=rejected,
        semantic_pairs_checked=len(pairs),
    )


def select_diverse_questions(
    candidates: list[GeneratedQuestionItem], count: int
) -> list[GeneratedQuestionItem]:
    """Stable round-robin by topic/category after quality filtering."""
    buckets: OrderedDict[str, deque[GeneratedQuestionItem]] = OrderedDict()
    for candidate in candidates:
        key = normalize_question_text(candidate.topic or candidate.category or "general")
        buckets.setdefault(key, deque()).append(candidate)

    selected: list[GeneratedQuestionItem] = []
    while buckets and len(selected) < count:
        empty: list[str] = []
        for key, bucket in buckets.items():
            if bucket and len(selected) < count:
                selected.append(bucket.popleft())
            if not bucket:
                empty.append(key)
        for key in empty:
            buckets.pop(key, None)
    return selected
