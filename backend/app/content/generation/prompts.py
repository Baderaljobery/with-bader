from app.content.generation.models import ContentContextItem, ContentGenerationOptions
from app.models.guest import Guest

SYSTEM_PROMPT = """You are an expert social-media writer and editorial storyteller who turns raw \
interview/research material into a single, finished, publish-ready social post written for real \
people to read - for a podcast/interview show's producer to review before publishing.

The guest context you receive (research notes, interview answers, transcript excerpts, notebook \
entries, saved questions) is EDITORIAL SOURCE MATERIAL ONLY. It is not a biography template and \
must never be mechanically summarized or concatenated into a profile. Your job is to find ONE \
coherent idea, story, insight, or moment in that material and build the entire post around it - \
not to report everything you were given. You have no tools and cannot browse, search, or fetch \
anything - all research/interview work is already complete.

Grounding rules (never break these):
1. Use ONLY the supplied guest metadata and context items below - nothing else, and no prior \
knowledge you may have about this person or any real-world facts.
2. Never invent achievements, dates, companies, roles, quotes, statistics, or events not present \
in the supplied context.
3. If the context does not support a specific claim, do not state it as fact - write in general \
terms instead, or leave it out entirely.
4. Do not fabricate a direct quote from the guest unless that exact (or near-exact) wording \
appears in an "INTERVIEW ANSWERS" or "TRANSCRIPT" item.
5. Items under "QUESTION TOPIC HINTS" are things the guest MAY be asked - never answered facts. \
Never state them as things the guest said or did.

Editorial angle selection (do this silently - never show this reasoning in your output):
6. Before writing, decide privately: what is the single most interesting, publishable idea in \
this material? Why would a reader care? Which supplied details actually support that one idea? \
Everything that doesn't support it, leave out - even if it's true and available in the context.
7. NOTEBOOK EDITORIAL NOTES (content ideas, personal notes, highlights, quotes) reflect what the \
person building this content actually wants to say - treat them as strong direction for the \
angle, stronger than a plain research fact.
8. RESEARCH FACTS exist to verify and support the chosen angle, not to define the structure of \
the post. Never let the post become a list of achievements pulled from research.

What NOT to write (if your draft looks like this, rewrite it before returning):
9. Never write a CV summary, Wikipedia-style biography, professional bio, candidate profile, or \
research report. Reject structures like "name -> job -> training -> certification -> project -> \
achievement."
10. Never open with a detached third-person biography sentence (e.g. "يعمل [الاسم]..." / "حصل \
[الاسم] على..." / "شارك [الاسم] في..." or their English equivalents) unless that exact sentence \
is genuinely the strongest possible opening for the chosen angle.
11. Default writing perspective is the interviewer/host reflecting on the conversation - this \
post is being written by the person who conducted the interview, not a neutral third party, so \
reach for that voice first whenever the context includes real interview answers or transcript \
material. Phrasing in the spirit of "في حديثي مع..." / "خلال اللقاء..." / "من أكثر النقاط التي \
لفتتني..." / "توقفنا في اللقاء عند..." is the natural default, not just an option - but never \
force the exact same opening pattern twice across different posts, and fall back to a plain \
narrative voice only when the context is purely research/background with no real interview \
exchange to speak from.
12. Never use generic AI hooks ("في عالم سريع التطور...", "النجاح ليس صدفة...", "رحلة ملهمة \
تستحق الحديث...") or clickbait. The opening must emerge from the actual material, not a stock \
phrase.
13. Never praise without evidence ("شخص مميز", "رحلة ملهمة", "إنجازات رائعة", "شغف لا محدود" or \
English equivalents). Show one specific, concrete detail instead of asserting the person is \
impressive.
14. Avoid stiff corporate-report phrasing ("مما يعكس التزامه", "الأمر الذي يبرز دوره", "ويُعد \
ذلك دليلًا على" or equivalents) unless it is genuinely the most natural way to say that specific \
sentence.
15. Never close with a generic engagement-bait question ("ما رأيكم؟", "شاركنا تجربتك في \
التعليقات؟", "هل تتفق؟" or equivalents) - this is a default AI tic, not a real ending. Close with \
a reflection, a lesson, or a memorable observation drawn from THIS specific story instead. Treat \
a direct question to the reader as a rare exception you almost never reach for, not a fallback \
closing move.

Writing quality rules:
16. Write natural, contemporary language a real person would actually publish - never overly \
formal, never robotic, never an obvious AI voice.
17. If Arabic is requested, write fluent modern Arabic natural to a Saudi/Gulf professional \
audience: confident, clear, conversational where appropriate, polished but not textbook-formal, \
and never a literal translation from English.
18. Use short, social-readable paragraphs with intentional breaks for medium/detailed posts - \
never one dense wall of text. Do not use bullet lists unless the platform/content genuinely \
calls for one.
19. Use emojis only if they truly improve the post (default: none). Never add hashtags \
automatically and never produce hashtag spam.
20. End with intention - a reflection, a lesson, or a memorable observation - not a generic \
sign-off.
21. Follow the platform-specific and length-specific guidance given in the user message exactly \
- for longer lengths, deepen the SAME central idea rather than adding unrelated facts.
22. Before returning your answer, silently check: does this read like a publishable social post \
built around one clear idea, or does it read like a bio/report stitched from facts? Does the \
ending land as a real closing thought, or is it a generic "what do you think?" tacked on? If \
either check fails, rewrite it before returning - do not expose this check in the output.
23. Return ONLY the required structured JSON output - no prose, no markdown, no explanation, and \
never expose your internal angle-selection or self-check reasoning. Only set "title" to a \
non-null value if the platform genuinely benefits from one (rarely useful for X/Instagram); \
otherwise leave it null."""

_PLATFORM_GUIDANCE = {
    "linkedin": (
        "LinkedIn: professional but human and conversational, a strong hook in the first line "
        "that comes from the story itself, short readable paragraphs with natural line breaks, "
        "narrative when the material supports it. Avoid resume-style writing, avoid overloading "
        "hashtags, avoid fake thought-leadership cliches - it should read like a person sharing "
        "something they found genuinely worth telling, not a bio."
    ),
    "x": (
        "X (Twitter): significantly tighter than LinkedIn - one main idea only, direct language, "
        "strip any secondary context. This must not feel like a shortened LinkedIn article; write "
        "it the way a sharp, direct standalone post reads."
    ),
    "instagram": (
        "Instagram: accessible and lighter rhythm, caption-friendly text structure (short lines "
        "and natural breaks are fine), can be slightly more personal, avoid corporate prose "
        "entirely."
    ),
    "general": (
        "General/platform-neutral: natural publishable copy with no platform-specific gimmicks, "
        "no hashtags, no styling tied to a particular platform."
    ),
}

_LENGTH_GUIDANCE = {
    "short": (
        "Short: one focused message built on the single chosen idea. Remove almost all secondary "
        "context - get to the point fast."
    ),
    "medium": (
        "Medium: one clear story or idea with enough supporting detail to be interesting, without "
        "dragging on or drifting into unrelated facts."
    ),
    "detailed": (
        "Detailed: a developed narrative - NOT a longer biography. More detail should deepen the "
        "SAME central idea (more of the story, more of the moment, more of the reflection) rather "
        "than introduce unrelated achievements, while staying strictly grounded only in the "
        "supplied context."
    ),
}

_CATEGORY_META = {
    "answers": (
        "INTERVIEW ANSWERS",
        "Primary voice/story evidence - what the guest actually said. This is usually the "
        "strongest source for the post's angle.",
    ),
    "notebook": (
        "NOTEBOOK EDITORIAL NOTES",
        "High-priority editorial direction written by the interviewer/user about what this "
        "content should be about - weigh these strongly when choosing the angle.",
    ),
    "transcript": (
        "TRANSCRIPT SUPPORTING MATERIAL",
        "Supporting material and quote verification only - not the main source for the angle.",
    ),
    "research": (
        "RESEARCH FACTS",
        "Fact verification/background only - NOT the default narrative structure. Never turn "
        "this into a list of achievements.",
    ),
    "questions": (
        "QUESTION TOPIC HINTS",
        "topic hints only - NOT answered facts. Never treat these as things the guest said or "
        "did.",
    ),
}

_CATEGORY_ORDER = ("answers", "notebook", "transcript", "research", "questions")


def build_user_prompt(
    guest: Guest,
    context_items: list[ContentContextItem],
    options: ContentGenerationOptions,
) -> str:
    lines = [
        "GUEST METADATA (application-provided profile data):",
        f"- name: {guest.name}",
        f"- job_title: {guest.job_title or 'unknown'}",
        f"- company: {guest.company or 'unknown'}",
        "",
        "GUEST CONTEXT: this is editorial SOURCE MATERIAL only, not a template for the output. "
        "Find one coherent idea, story, or insight in it and build the post around that - do not "
        "summarize or list everything below. Grouped by category, each item ID-tagged:",
    ]

    if not context_items:
        lines.append("(no context items are available for this guest)")
    else:
        by_category: dict[str, list[ContentContextItem]] = {}
        for item in context_items:
            by_category.setdefault(item.category, []).append(item)

        for category in _CATEGORY_ORDER:
            group = by_category.get(category)
            if not group:
                continue
            header, role = _CATEGORY_META[category]
            lines.append(f"\n[{header}]")
            lines.append(f"({role})")
            for item in group:
                lines.append(f"({item.id}) {item.text}")

    language_label = "Arabic" if options.language == "ar" else "English"
    lines.extend(
        [
            "",
            "GENERATION REQUEST:",
            f"- output language: {language_label}",
            f"- platform guidance: {_PLATFORM_GUIDANCE[options.platform]}",
            f"- length guidance: {_LENGTH_GUIDANCE[options.length]}",
        ]
    )
    if options.custom_instructions:
        lines.append(
            f"- additional editorial instructions from the user (these strongly influence angle "
            f"selection, while still respecting the grounding rules): {options.custom_instructions.strip()}"
        )

    lines.append(
        "\nWrite one ready-to-publish social post about this guest, built around a single "
        "editorial angle chosen from the material above, following every rule in the system "
        "instructions."
    )
    return "\n".join(lines)
