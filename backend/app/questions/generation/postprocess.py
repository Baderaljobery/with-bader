from app.questions.generation.groq_models import GroqQuestionGenerationSchema
from app.questions.generation.models import GeneratedQuestionItem, ResearchContextItem


def _resolve_research_ids(
    research_item_ids: list[str], indexed: dict[str, ResearchContextItem]
) -> tuple[list[str], list[str]]:
    """Keep only IDs that were actually supplied to the model; resolve them
    to durable URLs. An LLM-authored URL is never trusted - only IDs we
    ourselves handed out, mapped back through our own research-item index."""
    valid_ids: list[str] = []
    urls: list[str] = []
    seen: set[str] = set()

    for research_id in research_item_ids or []:
        item = indexed.get(research_id)
        if item is None:
            continue
        valid_ids.append(research_id)
        for url in item.source_urls:
            if url not in seen:
                urls.append(url)
                seen.add(url)

    return valid_ids, urls


def _normalize_text(text: str) -> str:
    normalized = " ".join(text.strip().lower().split())
    return normalized.rstrip("؟?.!،, ")


def _tokenize(text: str) -> set[str]:
    return set(_normalize_text(text).split())


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    union = len(a | b)
    return intersection / union if union else 0.0


def _richness(item: GeneratedQuestionItem) -> tuple:
    return (len(item.research_item_ids), len(item.reason or ""))


def _dedupe_questions(
    items: list[GeneratedQuestionItem], similarity_threshold: float = 0.82
) -> list[GeneratedQuestionItem]:
    """Collapse exact and near-identical questions (by normalized word-set
    overlap) without another LLM call, keeping the more grounded/richer
    question of each duplicate pair."""
    kept: list[GeneratedQuestionItem] = []
    kept_tokens: list[set[str]] = []

    for item in items:
        tokens = _tokenize(item.text)
        duplicate_index = next(
            (
                i
                for i, existing_tokens in enumerate(kept_tokens)
                if _jaccard_similarity(tokens, existing_tokens) >= similarity_threshold
            ),
            None,
        )

        if duplicate_index is None:
            kept.append(item)
            kept_tokens.append(tokens)
        elif _richness(item) > _richness(kept[duplicate_index]):
            kept[duplicate_index] = item
            kept_tokens[duplicate_index] = tokens

    return kept


def build_generated_questions(
    schema_result: GroqQuestionGenerationSchema,
    indexed_research: dict[str, ResearchContextItem],
) -> list[GeneratedQuestionItem]:
    """Convert the raw (LLM-produced) schema into the trusted output shape:
    invalid research_item_ids stripped, questions whose citations were all
    invalid dropped (a question that never claimed any citation is kept -
    see research_item_ids semantics in prompts.py rule 8), IDs resolved to
    durable source_urls, near-duplicates collapsed."""
    processed: list[GeneratedQuestionItem] = []

    for raw in schema_result.questions:
        text = raw.text.strip()
        if not text:
            continue

        original_ids = list(raw.research_item_ids or [])
        valid_ids, urls = _resolve_research_ids(original_ids, indexed_research)

        if original_ids and not valid_ids:
            # Every citation the model gave was fake/invalid - the specific
            # claim behind this question is now unsupported. Drop it.
            continue

        processed.append(
            GeneratedQuestionItem(
                text=text,
                topic=raw.topic,
                category=raw.category,
                priority=raw.priority,
                research_item_ids=valid_ids,
                source_urls=urls,
                reason=raw.reason,
                follow_up_questions=list(raw.follow_up_questions or []),
            )
        )

    return _dedupe_questions(processed)
