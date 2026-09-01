import unittest
from types import SimpleNamespace

from app.questions.generation.research_context import build_research_context


def _fake_research(**fields) -> SimpleNamespace:
    defaults = dict(
        career_history=[],
        achievements=[],
        projects=[],
        interesting_events=[],
        potential_interview_angles=[],
        sources=[{"url": "https://should-never-be-read.example", "content": "x" * 10000}],
    )
    defaults.update(fields)
    return SimpleNamespace(**defaults)


class ResearchContextBuilderTests(unittest.TestCase):
    def test_career_history_item_becomes_fact_with_source_urls(self):
        research = _fake_research(
            career_history=[
                {
                    "role": "CEO",
                    "company": "Example Co",
                    "start_date": "2019",
                    "end_date": None,
                    "source_urls": ["https://example.org/a"],
                }
            ]
        )
        items = build_research_context(research)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "R1")
        self.assertEqual(items[0].item_type, "career_history")
        self.assertIn("CEO", items[0].fact)
        self.assertEqual(items[0].source_urls, ["https://example.org/a"])

    def test_never_reads_raw_sources_field(self):
        research = _fake_research(
            achievements=[{"title": "Did a thing", "source_urls": ["https://a.example"]}]
        )
        items = build_research_context(research)
        combined_text = " ".join(item.fact for item in items)
        self.assertNotIn("should-never-be-read", combined_text)

    def test_items_without_required_fields_are_skipped(self):
        research = _fake_research(achievements=[{"title": None}, {}])
        self.assertEqual(build_research_context(research), [])

    def test_ids_assigned_sequentially_across_types(self):
        research = _fake_research(
            achievements=[{"title": "Achievement A"}],
            projects=[{"title": "Project B"}],
        )
        items = build_research_context(research)
        self.assertEqual([item.id for item in items], ["R1", "R2"])

    def test_respects_max_items(self):
        research = _fake_research(
            achievements=[{"title": f"Achievement {i}"} for i in range(10)]
        )
        items = build_research_context(research, max_items=3)
        self.assertEqual(len(items), 3)

    def test_respects_max_chars_but_keeps_at_least_one_item(self):
        research = _fake_research(achievements=[{"title": "x" * 5000}])
        items = build_research_context(research, max_chars=10)
        self.assertEqual(len(items), 1)

    def test_empty_research_returns_empty_context(self):
        research = _fake_research()
        self.assertEqual(build_research_context(research), [])

    def test_missing_source_urls_defaults_to_empty_list(self):
        research = _fake_research(achievements=[{"title": "No sources listed"}])
        items = build_research_context(research)
        self.assertEqual(items[0].source_urls, [])


if __name__ == "__main__":
    unittest.main()
