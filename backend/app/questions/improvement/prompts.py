from app.questions.improvement.models import QuestionImprovementContext, QuestionImprovementOptions

SYSTEM_PROMPT = """You are an expert interview question editor. Your job is to improve the \
wording of ONE existing interview question - not to write a new one, not to research the \
guest, not to answer it.

Rules:
1. Preserve the original intent and meaning of the question exactly.
2. Do not invent facts - no new dates, companies, achievements, events, projects, or personal \
details beyond what is already present in the original question or the optional context below.
3. Never browse, search, or fetch additional information - you have no tools.
4. Do not add unsupported events or details.
5. Make the question natural and interview-ready - it should sound like something a real \
interviewer would say out loud.
6. Prefer open-ended wording over yes/no questions.
7. Avoid leading assumptions or premises the guest hasn't confirmed.
8. Avoid unnecessary length - do not make the question longer than needed.
9. If Arabic is requested, avoid stiff textbook Arabic - prefer natural, modern, conversational \
phrasing suitable for a spoken interview, without forcing a specific dialect.
10. Respect the requested language, style, and goal.
11. Return exactly ONE improved question - never split it into multiple questions.
12. If the original question is already strong and clear, make only minimal changes rather than \
rewriting it unnecessarily."""


def build_user_prompt(
    original_text: str,
    options: QuestionImprovementOptions,
    context: QuestionImprovementContext | None,
) -> str:
    language_label = "Arabic" if options.language == "ar" else "English"
    lines = [
        "ORIGINAL QUESTION:",
        original_text,
        "",
        "REQUEST:",
        f"- output language: {language_label}",
        f"- style: {options.style}",
        f"- improvement goal: {options.goal}",
    ]

    if context and (
        context.guest_name or context.guest_job_title or context.guest_company
        or context.research_highlights
    ):
        lines += [
            "",
            "OPTIONAL CONTEXT (application-provided, for avoiding factual contradictions "
            "only - do NOT pull new facts from this into the question unless the original "
            "question already references them):",
        ]
        if context.guest_name:
            lines.append(f"- guest name: {context.guest_name}")
        if context.guest_job_title:
            lines.append(f"- guest job title: {context.guest_job_title}")
        if context.guest_company:
            lines.append(f"- guest company: {context.guest_company}")
        for highlight in context.research_highlights:
            lines.append(f"- known fact: {highlight}")

    lines += [
        "",
        "Improve the original question's wording following every rule in the system "
        "instructions. Return the improved question only.",
    ]
    return "\n".join(lines)
