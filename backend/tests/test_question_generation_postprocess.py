import unittest

from app.questions.generation.groq_models import (
    GroqGeneratedQuestionItem,
    GroqQuestionGenerationSchema,
)
from app.questions.generation.models import ResearchContextItem
from app.questions.generation.postprocess import build_generated_questions


def _indexed(*urls: str) -> dict[str, ResearchContextItem]:
    return {
        f"R{i + 1}": ResearchContextItem(
            id=f"R{i + 1}", item_type="career_history", fact=f"Fact {i + 1}", source_urls=[url]
        )
        for i, url in enumerate(urls)
    }


class ResearchIdValidationTests(unittest.TestCase):
    def test_valid_research_ids_resolve_to_source_urls(self):
        indexed = _indexed("https://example.org/a", "https://example.org/b")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="What changed after that transition?",
                    category="turning_point",
                    research_item_ids=["R1", "R2"],
                )
            ]
        )
        [question] = build_generated_questions(schema, indexed)
        self.assertEqual(question.research_item_ids, ["R1", "R2"])
        self.assertEqual(
            question.source_urls, ["https://example.org/a", "https://example.org/b"]
        )

    def test_invalid_research_ids_are_removed(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="Tell us about that moment?",
                    category="turning_point",
                    research_item_ids=["R1", "R999", "UNKNOWN"],
                )
            ]
        )
        [question] = build_generated_questions(schema, indexed)
        self.assertEqual(question.research_item_ids, ["R1"])
        self.assertEqual(question.source_urls, ["https://example.org/a"])

    def test_question_with_zero_valid_ids_is_dropped(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="Fabricated grounded question?",
                    category="achievement",
                    research_item_ids=["R999"],
                )
            ]
        )
        self.assertEqual(build_generated_questions(schema, indexed), [])

    def test_generic_question_with_no_ids_from_start_is_kept(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="What drives you day to day?",
                    category="personal_perspective",
                    research_item_ids=[],
                )
            ]
        )
        questions = build_generated_questions(schema, indexed)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].research_item_ids, [])


class DuplicateRemovalTests(unittest.TestCase):
    def test_exact_duplicate_questions_collapse(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="What changed after the transition?",
                    category="turning_point",
                    research_item_ids=["R1"],
                ),
                GroqGeneratedQuestionItem(
                    text="What changed after the transition?",
                    category="turning_point",
                    research_item_ids=["R1"],
                ),
            ]
        )
        self.assertEqual(len(build_generated_questions(schema, indexed)), 1)

    def test_near_identical_questions_collapse_keeping_richer(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="What changed in your approach after the transition happened?",
                    category="turning_point",
                    research_item_ids=[],
                ),
                GroqGeneratedQuestionItem(
                    text="What changed in your approach after the transition happened",
                    category="turning_point",
                    research_item_ids=["R1"],
                    reason="Grounded in career history",
                ),
            ]
        )
        questions = build_generated_questions(schema, indexed)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].research_item_ids, ["R1"])

    def test_distinct_questions_are_preserved(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[
                GroqGeneratedQuestionItem(
                    text="What changed after the transition?",
                    category="turning_point",
                    research_item_ids=["R1"],
                ),
                GroqGeneratedQuestionItem(
                    text="How do you approach hiring decisions?",
                    category="leadership",
                    research_item_ids=["R1"],
                ),
            ]
        )
        self.assertEqual(len(build_generated_questions(schema, indexed)), 2)


class EmptyTextTests(unittest.TestCase):
    def test_blank_question_text_is_dropped(self):
        indexed = _indexed("https://example.org/a")
        schema = GroqQuestionGenerationSchema(
            questions=[GroqGeneratedQuestionItem(text="   ", category="career_journey")]
        )
        self.assertEqual(build_generated_questions(schema, indexed), [])


if __name__ == "__main__":
    unittest.main()
