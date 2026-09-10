import unittest

from app.research.identity_resolution import (
    aggregate_identity_relevance,
    score_identity_relevance,
)
from app.research.models import NormalizedResearchSource
from app.research.research_planner import _PlannedQueryItem, _validate_planned_queries
from app.research.collectors.link_content_fetcher import (
    _is_disallowed_host,
    _is_safe_public_url,
    should_skip_deep_fetch,
)
from tests.db_test_helpers import FakeGuestIdentity


class IdentityRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.guest = FakeGuestIdentity(
            name_ar="أحمد مثال",
            name_en="Ahmed Example",
            company="Example Co",
        )

    def test_unrelated_source_scores_low(self):
        source = NormalizedResearchSource(
            source_type="website",
            title="Totally unrelated headline",
            content="Nothing to do with this person or their company.",
        )
        self.assertLess(score_identity_relevance(source, self.guest), 0.2)

    def test_name_match_scores_higher_than_company_only(self):
        name_match = NormalizedResearchSource(
            source_type="website", title="Ahmed Example wins an award"
        )
        company_only = NormalizedResearchSource(
            source_type="website", title="Example Co posts quarterly earnings"
        )
        self.assertGreater(
            score_identity_relevance(name_match, self.guest),
            score_identity_relevance(company_only, self.guest),
        )

    def test_trusted_guest_link_gets_high_floor_even_without_text(self):
        source = NormalizedResearchSource(
            source_type="linkedin",
            url="https://linkedin.com/in/someone",
            metadata={"origin": "guest_link"},
        )
        self.assertGreaterEqual(score_identity_relevance(source, self.guest), 0.8)

    def test_aggregate_relevance_of_empty_list_is_zero(self):
        self.assertEqual(aggregate_identity_relevance([], self.guest), 0.0)


class QueryPlanValidationTests(unittest.TestCase):
    def setUp(self):
        self.guest = FakeGuestIdentity(name_ar="أحمد مثال", name_en="Ahmed Example")

    def test_rejects_blank_query(self):
        items = [_PlannedQueryItem(objective="career", language="en", query="   ")]
        result = _validate_planned_queries(items, self.guest, set(), budget=5)
        self.assertEqual(result, [])

    def test_rejects_duplicate_of_existing_query(self):
        items = [_PlannedQueryItem(objective="career", language="en", query="Ahmed Example career")]
        already_seen = {"ahmed example career"}
        result = _validate_planned_queries(items, self.guest, already_seen, budget=5)
        self.assertEqual(result, [])

    def test_rejects_off_objective(self):
        items = [
            _PlannedQueryItem(objective="not_a_real_objective", language="en", query="Ahmed Example x")
        ]
        result = _validate_planned_queries(items, self.guest, set(), budget=5)
        self.assertEqual(result, [])

    def test_rejects_query_with_no_identity_anchor(self):
        items = [_PlannedQueryItem(objective="career", language="en", query="famous company news")]
        result = _validate_planned_queries(items, self.guest, set(), budget=5)
        self.assertEqual(result, [])

    def test_accepts_valid_grounded_query(self):
        items = [_PlannedQueryItem(objective="career", language="en", query="Ahmed Example promotion")]
        result = _validate_planned_queries(items, self.guest, set(), budget=5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].source, "ai_planner")

    def test_respects_budget(self):
        items = [
            _PlannedQueryItem(objective="career", language="en", query=f"Ahmed Example topic {i}")
            for i in range(10)
        ]
        result = _validate_planned_queries(items, self.guest, set(), budget=3)
        self.assertEqual(len(result), 3)


class LinkFetchSafetyTests(unittest.TestCase):
    def test_rejects_non_http_scheme(self):
        self.assertFalse(_is_safe_public_url("file:///etc/passwd"))

    def test_rejects_localhost_by_name(self):
        self.assertTrue(_is_disallowed_host("localhost"))

    def test_rejects_loopback_ip(self):
        self.assertTrue(_is_disallowed_host("127.0.0.1"))

    def test_rejects_private_network_ip(self):
        self.assertTrue(_is_disallowed_host("10.0.0.5"))
        self.assertTrue(_is_disallowed_host("192.168.1.1"))

    def test_allows_public_ip_literal(self):
        self.assertFalse(_is_disallowed_host("8.8.8.8"))

    def test_skips_deep_fetch_for_auth_walled_platforms(self):
        self.assertTrue(should_skip_deep_fetch("https://www.linkedin.com/in/someone"))
        self.assertTrue(should_skip_deep_fetch("https://youtube.com/watch?v=abc"))
        self.assertFalse(should_skip_deep_fetch("https://example.com/about"))


if __name__ == "__main__":
    unittest.main()
