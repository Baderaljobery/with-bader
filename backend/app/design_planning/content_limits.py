"""Per-template, per-role content budgets fed to the planner's prompt.

Mirrors frontend/features/design/templates/template-0*/config.ts exactly
(same numbers, same fields) - that is the renderer's own source of truth
for how much text each template/role combination actually has room for.
Templates render text at a FIXED size (no shrink-to-fit), so text longer
than these budgets gets visually clipped rather than resized - the planner
must write to fit, not the other way around (Part 11/12/13 of the Design
Engine rework: "the AI planner should receive those [template] content
limits constraints").
"""

from app.design_planning.models import SlideRole

ContentLimits = dict[str, int | None]

# The 4 known template ids - single source of truth (previously duplicated
# in the now-deleted app/design_generation/templates.py, which existed
# only to load reference images for the retired AI image-generation path).
# Anything validating a template_id (see app/schemas/design_generation.py)
# imports TEMPLATE_IDS from here.
_TEMPLATE_CONTENT_LIMITS: dict[str, dict[SlideRole, ContentLimits]] = {
    "template-01": {
        "cover": {"headline_max_chars": 60, "body_max_chars": 70, "max_points": None},
        "main_content": {"headline_max_chars": 50, "body_max_chars": 160, "max_points": None},
        "continuation": {"headline_max_chars": 40, "body_max_chars": 180, "max_points": None},
        "quote": {"headline_max_chars": 140, "body_max_chars": None, "max_points": None},
        "quick_points": {"headline_max_chars": 40, "body_max_chars": None, "max_points": 4},
        "closing": {"headline_max_chars": 60, "body_max_chars": 60, "max_points": None},
    },
    "template-02": {
        "cover": {"headline_max_chars": 44, "body_max_chars": 40, "max_points": None},
        "main_content": {"headline_max_chars": 36, "body_max_chars": 130, "max_points": None},
        "continuation": {"headline_max_chars": 30, "body_max_chars": 150, "max_points": None},
        "quote": {"headline_max_chars": 120, "body_max_chars": None, "max_points": None},
        "quick_points": {"headline_max_chars": 30, "body_max_chars": None, "max_points": 4},
        "closing": {"headline_max_chars": 40, "body_max_chars": 40, "max_points": None},
    },
    "template-03": {
        "cover": {"headline_max_chars": 24, "body_max_chars": None, "max_points": None},
        "main_content": {"headline_max_chars": 24, "body_max_chars": 90, "max_points": None},
        "continuation": {"headline_max_chars": 24, "body_max_chars": 90, "max_points": None},
        "quote": {"headline_max_chars": 90, "body_max_chars": None, "max_points": None},
        "quick_points": {"headline_max_chars": 20, "body_max_chars": None, "max_points": 4},
        "closing": {"headline_max_chars": 20, "body_max_chars": None, "max_points": None},
    },
    "template-04": {
        "cover": {"headline_max_chars": 26, "body_max_chars": 24, "max_points": None},
        "main_content": {"headline_max_chars": 22, "body_max_chars": 130, "max_points": None},
        "continuation": {"headline_max_chars": 22, "body_max_chars": 150, "max_points": None},
        "quote": {"headline_max_chars": 110, "body_max_chars": None, "max_points": None},
        "quick_points": {"headline_max_chars": 20, "body_max_chars": None, "max_points": 4},
        "closing": {"headline_max_chars": 22, "body_max_chars": 20, "max_points": None},
    },
}


TEMPLATE_IDS: tuple[str, ...] = tuple(_TEMPLATE_CONTENT_LIMITS.keys())


def get_content_limits(template_id: str, role: SlideRole) -> ContentLimits | None:
    return _TEMPLATE_CONTENT_LIMITS.get(template_id, {}).get(role)
