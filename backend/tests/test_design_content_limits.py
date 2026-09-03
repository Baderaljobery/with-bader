import unittest

from app.design_generation.templates import TEMPLATE_IDS
from app.design_planning.content_limits import get_content_limits
from app.design_planning.models import PlanContextItem, SlidePlanningOptions, SlideRoleSpec
from app.design_planning.prompts import build_user_prompt
from app.models.design_slide import DESIGN_SLIDE_ROLES


class ContentLimitsTests(unittest.TestCase):
    def test_every_real_template_defines_limits_for_every_role(self):
        """Part 11: the planner must be able to look up a budget for any
        (template, role) combination the user can actually request - a
        missing entry would silently fall back to "no limit", so this
        guards against a template being added without content limits."""
        for template_id in TEMPLATE_IDS:
            for role in DESIGN_SLIDE_ROLES:
                limits = get_content_limits(template_id, role)
                self.assertIsNotNone(limits, f"missing content limits for {template_id}/{role}")
                self.assertGreater(limits["headline_max_chars"], 0)

    def test_unknown_template_returns_none(self):
        self.assertIsNone(get_content_limits("not-a-real-template", "cover"))


class PromptContentLimitInjectionTests(unittest.TestCase):
    def _guest(self):
        class _Guest:
            name = "ضيف تجريبي"
            job_title = None
            company = None

        return _Guest()

    def test_prompt_includes_the_selected_templates_real_budget(self):
        """The tight template-03 budget (headline <= 24 for cover) must
        show up verbatim in the prompt sent to the model - and must differ
        from template-01's much larger budget for the same role/slide,
        proving the limit is genuinely template-specific, not a generic
        role-only number (Part 11)."""
        options_tight = SlidePlanningOptions(
            platform="linkedin",
            slide_roles=[SlideRoleSpec(index=1, role="cover")],
            template_id="template-03",
        )
        options_roomy = SlidePlanningOptions(
            platform="linkedin",
            slide_roles=[SlideRoleSpec(index=1, role="cover")],
            template_id="template-01",
        )
        context = [PlanContextItem(id="C1", category="content_draft", text="نص تجريبي.")]

        tight_prompt = build_user_prompt(self._guest(), context, options_tight)
        roomy_prompt = build_user_prompt(self._guest(), context, options_roomy)

        self.assertIn("headline <= 24 chars", tight_prompt)
        self.assertIn("headline <= 60 chars", roomy_prompt)
        self.assertNotIn("headline <= 24 chars", roomy_prompt)

    def test_quick_points_budget_includes_max_points(self):
        options = SlidePlanningOptions(
            platform="linkedin",
            slide_roles=[SlideRoleSpec(index=1, role="quick_points")],
            template_id="template-02",
        )
        prompt = build_user_prompt(self._guest(), [], options)
        self.assertIn("max 4 points", prompt)


if __name__ == "__main__":
    unittest.main()
