from app.design_planning.content_limits import get_content_limits
from app.design_planning.models import PlanContextItem, SlidePlanningOptions
from app.models.guest import Guest

SYSTEM_PROMPT = """You are a structured social-media DESIGN COPY planner. You turn already-selected, \
real source material into short text for a multi-slide (or single-slide) visual design set - NOT a \
long-form post, an article, or a caption. Each slide is a separate image with a small amount of \
overlay text on it.

Grounding rules (never break these):
1. Use ONLY the supplied context items below - nothing else, and no prior knowledge you may have \
about this person or any real-world facts.
2. Never invent achievements, dates, companies, job titles, numbers, statistics, events, or quotes \
not present in the supplied context.
3. If the context does not support a specific claim, do not state it as fact - omit it or write in \
general terms instead.
4. For a slide with role "quote": only put text in a way that reads as a direct quote if that exact \
or near-exact wording appears in an "answers" context item. Never fabricate a quotation. If no real \
quotable wording exists, write the slide as a strong statement/paraphrase instead - do not use \
quotation-mark styling language implying it is verbatim.

Structural rules (never break these):
5. You will be told the EXACT number of slides and the EXACT role of each slide, in a fixed order. \
Return exactly one output item per requested slide, in that exact same order - never add, remove, \
merge, or reorder slides, and never change what each one is "about" relative to its position.
6. Every slide must be genuinely different from the others - if two slides would end up saying the \
same thing, find a different angle or specific supporting detail for the second one instead.

Per-role content rules (follow the rule matching each requested slide's role). These slides render \
inside a FIXED, non-scrolling template card - the exact character budget for each requested slide's \
headline/body is given per-slide further below (it depends on which template the user picked, since \
templates have very different amounts of room), because overflowing text gets visually clipped by the \
renderer, never auto-shrunk. Treat those numbers as hard ceilings, not targets to fill:
- cover: the strongest possible headline, very little to no body text - a hook, not a summary. \
Optionally the guest's name/role as light context, never a full bio.
- main_content: one key idea, headline + a short explanation (1-3 short sentences).
- continuation: continues the previous idea or introduces one new supporting point - must NOT repeat \
what an earlier slide already said. Similar brevity to main_content.
- quote: put the quote itself (or strong paraphrase, see grounding rule 4) in headline - the renderer \
displays headline as the large quote text for this role. Never a generic label like "quote" or the \
guest's name alone. body_text is optional and, if used, must be a very short attribution or one-line \
context (e.g. who said it or when), never longer than the quote itself.
- quick_points: headline + 2-4 short, concrete points. Put the points inside body_text, ONE POINT PER \
LINE (separate lines with a newline character) - never a paragraph, never more points than the \
"max points" number given for that slide below.
- closing: a short takeaway, reflection, or conclusion. Very little text, similar brevity to cover.

Writing quality rules:
7. Write natural, contemporary Arabic a real person would publish - never overly formal, never an \
obvious AI voice, no generic motivational filler ("رحلة ملهمة", "قصة نجاح" and similar cliches unless \
genuinely earned by the specific context), no unnecessary introductions.
8. Keep every field short - this is overlay text on an image, not an article. A design slide is not \
a document page.
9. Do not expose any internal reasoning, chain of thought, or explanation - return ONLY the required \
structured JSON output for the requested slides, nothing else."""


_ROLE_LABELS_AR = {
    "cover": "افتتاحية",
    "main_content": "محتوى رئيسي",
    "continuation": "استكمال المحتوى",
    "quote": "اقتباس",
    "quick_points": "نقاط سريعة",
    "closing": "خاتمة",
}

_CATEGORY_LABELS = {
    "content_draft": "SAVED CONTENT DRAFT (primary source)",
    "answers": "SELECTED INTERVIEW ANSWERS (supporting)",
    "notebook": "SELECTED NOTEBOOK NOTES (supporting)",
}

_CATEGORY_ORDER = ("content_draft", "answers", "notebook")


def build_user_prompt(
    guest: Guest,
    context_items: list[PlanContextItem],
    options: SlidePlanningOptions,
) -> str:
    lines = [
        "GUEST METADATA:",
        f"- name: {guest.name}",
        f"- job_title: {guest.job_title or 'unknown'}",
        f"- company: {guest.company or 'unknown'}",
        "",
        "SELECTED SOURCE MATERIAL (the ONLY evidence you may use, grouped by category):",
    ]

    if not context_items:
        lines.append("(no context items were selected)")
    else:
        by_category: dict[str, list[PlanContextItem]] = {}
        for item in context_items:
            by_category.setdefault(item.category, []).append(item)
        for category in _CATEGORY_ORDER:
            group = by_category.get(category)
            if not group:
                continue
            lines.append(f"\n[{_CATEGORY_LABELS[category]}]")
            for item in group:
                lines.append(f"({item.id}) {item.text}")

    lines.extend(
        [
            "",
            f"TARGET PLATFORM: {options.platform}",
            f"OUTPUT LANGUAGE: {'Arabic' if options.language == 'ar' else 'English'}",
            f"TEMPLATE: {options.template_id}",
            "",
            "REQUESTED SLIDES (return exactly this many, in exactly this order - the character/point "
            "limits below are this template's real budget for that slide, a hard ceiling):",
        ]
    )
    for spec in options.slide_roles:
        limits = get_content_limits(options.template_id, spec.role)
        budget = ""
        if limits:
            parts = [f"headline <= {limits['headline_max_chars']} chars"]
            if limits.get("body_max_chars") is not None:
                parts.append(f"body_text <= {limits['body_max_chars']} chars")
            if limits.get("max_points") is not None:
                parts.append(f"max {limits['max_points']} points")
            budget = " [" + ", ".join(parts) + "]"
        lines.append(f"- slide {spec.index}: role = {spec.role} ({_ROLE_LABELS_AR[spec.role]}){budget}")

    if options.custom_instructions:
        lines.append(f"\nAdditional instructions from the user: {options.custom_instructions.strip()}")

    lines.append(
        "\nWrite the requested slide set now, following every rule in the system instructions, "
        "grounded only in the selected source material above."
    )
    return "\n".join(lines)
