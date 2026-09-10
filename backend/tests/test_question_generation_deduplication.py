import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

from app.core.config import settings
from app.questions.generation.base import QuestionGenerator
from app.questions.generation.deduplication import filter_unique_candidates
from app.questions.generation.engine import QuestionGenerationEngine
from app.questions.generation.models import (
    ExistingQuestionItem,
    GeneratedQuestionItem,
    QuestionGenerationOptions,
    QuestionGenerationResult,
    SemanticComparisonDecision,
)
from app.questions.generation.similarity import normalize_question_text


def _question(
    text: str,
    *,
    topic: str = "career",
    intent: str = "",
    research_ids: list[str] | None = None,
) -> GeneratedQuestionItem:
    return GeneratedQuestionItem(
        text=text,
        topic=topic,
        category=topic,
        intent_summary=intent,
        research_item_ids=research_ids or [],
    )


class _SemanticFake(QuestionGenerator):
    provider_name = "semantic-fake"

    def __init__(self, classification: str):
        self.classification = classification
        self.received_pairs = []

    async def generate(self, guest, research_items, options, existing_questions=None):
        return QuestionGenerationResult()

    async def classify_duplicate_pairs(self, pairs):
        self.received_pairs.extend(pairs)
        return [
            SemanticComparisonDecision(
                pair_id=pair.id, classification=self.classification
            )
            for pair in pairs
        ]


async def _filter(candidates, existing, generator):
    return await filter_unique_candidates(
        candidates,
        existing,
        generator,
        lexical_duplicate_threshold=0.88,
        intent_duplicate_threshold=0.82,
        semantic_candidate_threshold=0.12,
        max_semantic_pairs=80,
    )


class ArabicNormalizationTests(unittest.TestCase):
    def test_diacritics_tatweel_alef_and_punctuation_normalize(self):
        decorated = "مَــا الَّذِي أَلْهَمَكَ؟"
        plain = "ما الذي الهمك"
        self.assertEqual(normalize_question_text(decorated), normalize_question_text(plain))


class LayeredDuplicateTests(unittest.IsolatedAsyncioTestCase):
    async def test_exact_duplicate_inside_batch_is_removed(self):
        generator = _SemanticFake("DIFFERENT")
        result = await _filter(
            [_question("What changed?"), _question("What changed?")], [], generator
        )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.rejected), 1)

    async def test_punctuation_only_duplicate_is_removed(self):
        result = await _filter(
            [_question("What changed?!"), _question("What changed")],
            [],
            _SemanticFake("DIFFERENT"),
        )
        self.assertEqual(len(result.accepted), 1)

    async def test_arabic_normalized_duplicate_is_removed(self):
        result = await _filter(
            [_question("مَــا الَّذِي أَلْهَمَكَ؟"), _question("ما الذي الهمك")],
            [],
            _SemanticFake("DIFFERENT"),
        )
        self.assertEqual(len(result.accepted), 1)

    async def test_real_arabic_semantic_paraphrase_is_removed(self):
        existing = [
            ExistingQuestionItem(
                id="Q1",
                source="ai_generated",
                topic="career",
                text=(
                    "ما الذي ألهمك للتحول من محلل عمليات في بوينغ إلى عالم "
                    "البيانات في موزن؟"
                ),
            )
        ]
        candidate = _question(
            "ما الذي دفعك للانتقال من دور محلل عمليات في شركة Boeing إلى مسار علم البيانات في MOZN؟",
            topic="career",
            intent="الدافع وراء الانتقال من عمليات بوينغ إلى علم البيانات في موزن",
        )
        generator = _SemanticFake("DUPLICATE")
        result = await _filter([candidate], existing, generator)
        self.assertEqual(result.accepted, [])
        self.assertEqual(len(generator.received_pairs), 1)

    async def test_english_semantic_paraphrase_is_removed(self):
        existing = [
            ExistingQuestionItem(
                id="Q1",
                source="manual",
                topic="career",
                text="What inspired your move from Boeing operations to data science at MOZN?",
            )
        ]
        candidate = _question(
            "What motivated you to leave an operations role at Boeing for a data science path at MOZN?",
            topic="career",
            intent="motivation for Boeing to MOZN data science transition",
        )
        result = await _filter([candidate], existing, _SemanticFake("DUPLICATE"))
        self.assertEqual(result.accepted, [])

    async def test_same_topic_different_angle_is_preserved(self):
        existing = [
            ExistingQuestionItem(
                id="Q1",
                source="ai_generated",
                topic="predictive maintenance",
                text="كيف بدأت فكرة بحث الصيانة التنبؤية؟",
                intent_summary="origin of predictive maintenance research idea",
            )
        ]
        candidate = _question(
            "ما أكبر تحدٍ واجهكم عند تطبيق الصيانة التنبؤية في البيئة الصناعية؟",
            topic="predictive maintenance",
            intent="industrial implementation challenges",
        )
        generator = _SemanticFake("SAME_TOPIC_DIFFERENT_ANGLE")
        result = await _filter([candidate], existing, generator)
        self.assertEqual(result.accepted, [candidate])
        self.assertEqual(len(generator.received_pairs), 1)

    async def test_existing_manual_and_ai_questions_are_both_compared(self):
        candidate = _question("How did the project begin?", intent="project origin")
        for source in ("manual", "ai_generated"):
            with self.subTest(source=source):
                existing = [
                    ExistingQuestionItem(
                        id="Q1",
                        source=source,
                        text="How did the project begin?",
                        intent_summary="project origin",
                    )
                ]
                result = await _filter(
                    [candidate.model_copy(deep=True)],
                    existing,
                    _SemanticFake("DIFFERENT"),
                )
                self.assertEqual(result.accepted, [])


class _SequenceGenerator(QuestionGenerator):
    provider_name = "sequence"
    model_name = "test"

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def generate(self, guest, research_items, options, existing_questions=None):
        self.calls.append((options.count, list(existing_questions or [])))
        questions = self.responses.pop(0) if self.responses else []
        return QuestionGenerationResult(questions=questions)


def _research():
    return SimpleNamespace(
        id=uuid.uuid4(),
        version=1,
        career_history=[],
        education=[],
        achievements=[],
        projects=[],
        topics=[],
        interesting_events=[],
        public_appearances=[],
        potential_interview_angles=[],
    )


def _saved(text: str, source: str):
    return SimpleNamespace(
        id=uuid.uuid4(),
        text_=text,
        topic="career",
        source=source,
        intent_summary=None,
        research_item_ids=[],
        position=0,
        created_at=None,
    )


class CandidatePoolEngineTests(unittest.IsolatedAsyncioTestCase):
    def _patch_dependencies(self, saved=None):
        guest = SimpleNamespace(id=uuid.uuid4(), name="Guest", job_title="CEO", company="Co")
        research = _research()
        return (
            guest,
            research,
            patch("app.questions.generation.engine.guest_service.get_guest_by_id", return_value=guest),
            patch(
                "app.questions.generation.engine.guest_research_service.get_latest_guest_research",
                return_value=research,
            ),
            patch(
                "app.questions.generation.engine.question_service.get_questions",
                return_value=saved or [],
            ),
        )

    async def test_candidate_pool_is_larger_and_requested_count_is_returned(self):
        subjects = ["hiring", "education", "leadership", "research", "product", "future"]
        candidates = [
            _question(f"Tell us about {subject}?", topic=subject)
            for subject in subjects
        ]
        generator = _SequenceGenerator([candidates])
        guest, _, guest_patch, research_patch, questions_patch = self._patch_dependencies()
        with (
            guest_patch,
            research_patch,
            questions_patch,
            patch.object(settings, "question_generation_candidate_multiplier", 1.5),
        ):
            result = await QuestionGenerationEngine(generator).generate_questions(
                guest.id,
                object(),
                QuestionGenerationOptions(
                    count=4,
                    language="en",
                    style="deep",
                    include_followups=False,
                ),
            )
        self.assertEqual(generator.calls[0][0], 6)
        self.assertEqual(result.candidate_count, 6)
        self.assertEqual(result.generated_count, 4)

    async def test_one_bounded_refill_fills_the_requested_count(self):
        saved = [_saved("Existing question?", "manual")]
        generator = _SequenceGenerator(
            [
                [_question("Existing question?"), _question("Fresh one?", topic="one")],
                [_question("Fresh two?", topic="two")],
            ]
        )
        guest, _, guest_patch, research_patch, questions_patch = self._patch_dependencies(saved)
        with guest_patch, research_patch, questions_patch:
            result = await QuestionGenerationEngine(generator).generate_questions(
                guest.id,
                object(),
                QuestionGenerationOptions(
                    count=2,
                    language="en",
                    style="deep",
                    include_followups=False,
                ),
            )
        self.assertEqual(len(generator.calls), 2)
        self.assertEqual(result.refill_attempts, 1)
        self.assertEqual(result.generated_count, 2)

    async def test_returns_fewer_instead_of_lowering_duplicate_standard(self):
        saved = [_saved("Already covered?", "ai_generated")]
        generator = _SequenceGenerator(
            [[_question("Already covered?")], [_question("Already covered!")]]
        )
        guest, _, guest_patch, research_patch, questions_patch = self._patch_dependencies(saved)
        with guest_patch, research_patch, questions_patch:
            result = await QuestionGenerationEngine(generator).generate_questions(
                guest.id,
                object(),
                QuestionGenerationOptions(
                    count=3,
                    language="en",
                    style="deep",
                    include_followups=False,
                ),
            )
        self.assertEqual(result.generated_count, 0)
        self.assertEqual(result.refill_attempts, 1)

    async def test_saved_manual_and_ai_questions_reach_generator_prompt_context(self):
        saved = [_saved("Manual existing?", "manual"), _saved("AI existing?", "ai_generated")]
        generator = _SequenceGenerator([[]])
        guest, _, guest_patch, research_patch, questions_patch = self._patch_dependencies(saved)
        with guest_patch, research_patch, questions_patch:
            await QuestionGenerationEngine(generator).generate_questions(
                guest.id,
                object(),
                QuestionGenerationOptions(
                    count=1,
                    language="en",
                    style="deep",
                    include_followups=False,
                ),
            )
        sources = {item.source for item in generator.calls[0][1]}
        self.assertEqual(sources, {"manual", "ai_generated"})


if __name__ == "__main__":
    unittest.main()
