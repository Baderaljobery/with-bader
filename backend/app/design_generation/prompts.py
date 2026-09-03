from app.design_generation.models import SlideImageOptions, SupportingContextItem
from app.models.guest import Guest

_NO_TEXT_RULE = (
    "ABSOLUTE RULE - NO TEXT IN THIS IMAGE: Render ZERO letters, words, numbers, captions, "
    "labels, logos, watermarks, or typography of any kind, in any language or alphabet, "
    "anywhere in the frame - not even a single character, and not even something short or "
    "decorative. This image is pure visual artwork: shapes, gradients, light, texture, "
    "atmosphere - nothing written. A real Arabic headline and body text will be added on top "
    "of this image afterward by the application as separate, crisp HTML/CSS - if you render "
    "any text yourself, it will not match, will look like broken/garbled glyphs sitting right "
    "next to the real typography, and will ruin the result. Treat any impulse to add a "
    "headline, caption, or label as a mistake to avoid."
)

_BRAND_IDENTITY = (
    "Brand: With Bader (ويذ بدر), an Arabic-first professional "
    "interview-preparation and content platform. Visual identity: a signature teal-to-blue "
    "gradient (#1FCFC3 to #1B8FEA) used as a restrained accent, not a paint bucket. Overall "
    "tone: modern, premium, calm SaaS/editorial - the visual equivalent of a serious "
    "professional tool a podcaster trusts daily, never playful, never corporate-cold, never "
    "cluttered or stock-photo generic."
)

_REFERENCE_USAGE_RULE = (
    "An attached reference image is included below. Use it ONLY as inspiration for visual "
    "hierarchy, composition, spacing/whitespace, shape language, and overall visual rhythm - "
    "study how it balances empty space against visual interest, and echo that balance. Do "
    "NOT reproduce, trace, or closely copy the reference's exact text, logos, brand marks, "
    "photography, or specific third-party visual identity. Do not recreate it - adapt its "
    "compositional spirit into an ORIGINAL image using With Bader's own identity described "
    "above (its own colors and mood, not the reference's)."
)

_COMPOSITION_RULE = (
    "This image is a VISUAL BACKGROUND LAYER ONLY. Generate a clean, elegant visual "
    "composition - abstract shapes, soft gradients, subtle geometry, light, texture, "
    "atmosphere - with a clearly calm, low-texture, uncluttered empty zone deliberately left "
    "open in the area described below, sized and positioned to later receive external text "
    "that this image itself must NOT contain (see the no-text rule above)."
)

_PLATFORM_MOOD = {
    "linkedin": (
        "Platform mood: LinkedIn - professional and editorial, composed and trustworthy, "
        "subtle abstract geometry or soft gradient fields, corporate-safe but never sterile."
    ),
    "x": (
        "Platform mood: X (Twitter) - bold, high-contrast, energetic, one strong visual focal "
        "point, punchy but still elegant."
    ),
    "instagram": (
        "Platform mood: Instagram - warm and inviting, soft layered gradients, a lifestyle-"
        "friendly and slightly more personal atmosphere."
    ),
    "general": (
        "Platform mood: general-purpose - neutral, balanced, versatile enough to work across "
        "any platform, no platform-specific gimmicks."
    ),
}

# Role-specific composition briefs. These replace the old generic 4-way
# layout_type enum - the empty-zone placement/mood now varies by what this
# specific slide is FOR within the set (Part 18: one template supports
# multiple role variants, not one repeated composition).
_ROLE_COMPOSITION = {
    "cover": (
        "Slide role: COVER - the opening slide. Highly visual, the strongest single visual "
        "moment in the whole set. Reserve a smaller, clearly empty zone (e.g. lower third) for "
        "a short, bold headline only - most of the frame should be striking visual atmosphere, "
        "not empty space for a large text block."
    ),
    "main_content": (
        "Slide role: MAIN_CONTENT - carries one key idea. Reserve one large, calm, low-texture "
        "EMPTY zone (e.g. the lower half or one full side) - no shapes, no texture, no writing "
        "there - sized for a headline plus a short explanatory paragraph; concentrate visual "
        "interest in the remaining space."
    ),
    "continuation": (
        "Slide role: CONTINUATION - continues or supports the previous slide's idea. Similar "
        "empty-zone sizing to main_content, but the visual treatment should feel like a "
        "natural next beat in the same sequence, not a jarring restart - calmer, slightly more "
        "understated than the cover or main_content slide."
    ),
    "quote": (
        "Slide role: QUOTE - a centered, symmetrical, calm composition with a generous, "
        "completely EMPTY zone in the middle (no shapes, no texture, no writing there) sized "
        "for a short highlighted quote; a subtle decorative accent (soft abstract flourish, "
        "gentle light glow) framing that empty center is welcome, but the center itself must "
        "stay clean and uncluttered."
    ),
    "quick_points": (
        "Slide role: QUICK_POINTS - reserve a large, calm, low-texture EMPTY zone (no shapes, "
        "no texture, no writing there) sized for 2-4 short list-style lines stacked vertically; "
        "keep the visual portion simpler/quieter than a cover slide so the point list stays "
        "legible."
    ),
    "closing": (
        "Slide role: CLOSING - the final slide, a takeaway/reflection. Very little text is "
        "expected, so the empty zone should be small - most of the frame is visual atmosphere, "
        "ideally with a sense of resolution/calm rather than an obvious clone of the cover "
        "slide."
    ),
}


def _color_guidance(background_color: str, accent_color: str) -> str:
    return (
        f"Color direction: use {background_color} as the dominant background tone and "
        f"{accent_color} as a secondary/accent tone, blended tastefully with the brand's "
        "teal-to-blue gradient atmosphere - as soft surfaces and light gradients, not as flat "
        "literal paint fills. If these colors differ from the brand's default teal/blue, honor "
        "the user's chosen colors as the dominant palette while keeping the overall mood "
        "consistent with the brand identity above - never silently substitute a different "
        "palette."
    )


def build_slide_image_prompt(
    guest: Guest,
    options: SlideImageOptions,
    headline: str,
    body_text: str,
    supporting_context: list[SupportingContextItem],
) -> str:
    mood_lines = [f"Guest: {guest.name}"]
    if guest.job_title or guest.company:
        mood_lines.append(f"Role: {guest.job_title or ''} {('@ ' + guest.company) if guest.company else ''}".strip())
    if headline:
        mood_lines.append(f"Mood/subject reference, purely for visual inspiration, NOT text to draw: {headline}")
    if body_text:
        excerpt = body_text[:200]
        mood_lines.append(f"Additional mood reference, purely for visual inspiration, NOT text to draw: {excerpt}")
    for item in supporting_context[:3]:
        mood_lines.append(f"Related topic, purely for visual inspiration, NOT text to draw: {item.question}")

    lines = [
        _NO_TEXT_RULE,
        "",
        _BRAND_IDENTITY,
        "",
        _REFERENCE_USAGE_RULE,
        "",
        _COMPOSITION_RULE,
        "",
        _PLATFORM_MOOD[options.platform],
        _ROLE_COMPOSITION[options.role],
        _color_guidance(options.background_color, options.accent_color),
        "",
        "Mood/subject context (visual inspiration only - none of the following is text to "
        "render in the image):",
        *mood_lines,
        "",
        "Requirements: Arabic-audience professional social-media visual, RTL-friendly "
        "composition (safe to leave open space on the right as well as the left), modern, "
        "premium, elegant, minimal, social-media ready. This must be an original composition "
        "using With Bader's own identity - never a literal copy of the attached reference.",
    ]

    if options.custom_instructions:
        lines.append(f"Additional direction from the user: {options.custom_instructions.strip()}")

    lines.append(
        "\nFinal reminder: the image must contain absolutely no text, letters, numbers, or "
        "typography of any kind - a pure visual composition only, adapted from the reference's "
        "composition, never copying its text/logos/brand marks."
    )

    return "\n".join(lines)
