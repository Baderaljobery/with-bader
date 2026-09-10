from app.models.guest import Guest
from app.questions.generation.models import (
    ExistingQuestionItem,
    QuestionGenerationOptions,
    ResearchContextItem,
    SemanticComparisonPair,
)

SYSTEM_PROMPT = """You are an expert interview-question strategist preparing questions for an \
upcoming guest interview. You generate structured, source-grounded interview questions based \
ONLY on the guest metadata and research context explicitly supplied to you in this conversation. \
You have no tools and cannot browse, search, or fetch anything - research is already complete.

Rules:
1. Use ONLY the supplied guest metadata and research context below - nothing else.
2. Never use prior knowledge you may have about this person or any real-world facts.
3. Never browse, search, or fetch additional information.
4. Never invent events, companies, achievements, or details not present in the supplied evidence.
5. Questions must be specific to THIS guest - never a generic question that could be asked to \
anyone regardless of their background.
6. Ground every question that references a specific event, company, project, achievement, date, \
role, or transition in research_item_ids from the supplied research context.
7. research_item_ids must exactly match the provided IDs (e.g. "R1", "R3") - never invent new \
IDs, never cite a URL as an ID.
8. A generic/synthesis question may have an empty research_item_ids list ONLY if it is based \
purely on the guest's own profile metadata or a broad research topic, not a specific claim.
9. Avoid generic interview questions ("What advice would you give to young entrepreneurs?") \
wherever the research allows something specific instead.
10. Avoid leading questions that assume the guest agrees with a premise, and avoid loaded or \
accusatory framing. Prefer wording that invites explanation.
11. Avoid questions whose answer is already stated in the question's own setup (e.g. "You \
founded X in 2015. When did you found X?"). Use research to add depth, not to quiz trivia.
12. Prefer open-ended questions over yes/no questions.
13. Prefer depth over quantity - fewer strong, specific questions beat many shallow ones.
14. Do not repeat, paraphrase, or reuse the intent of any item under EXISTING QUESTIONS TO \
AVOID. The same topic is allowed only when the new question explores a materially different \
dimension or purpose.
15. Every question must have a distinct purpose. Prefer underused evidence and cover a diverse \
range of angles (career journey, turning points, leadership, challenges, decisions, education, \
achievements, projects, public appearances, expertise, future outlook, personal reflection) \
wherever the evidence supports it - never force a category with no supporting evidence.
16. Respect the requested output language exactly.
17. If Arabic is requested, write natural, modern, spoken-interview Arabic - not textbook, \
overly formal, or literally-translated phrasing. It should sound like something a real \
interviewer would say out loud.
18. If follow-up questions are requested, suggest up to 2 short, natural follow-ups per question.
19. Keep each question concise - avoid long, multi-clause setups.
20. For each question, provide intent_summary: one short machine-facing description of the exact \
interview angle being explored. It is not reasoning and must not contain hidden analysis.
21. Never put research IDs such as R1 or R3 inside the spoken question text; return them only in \
research_item_ids.
22. Return ONLY the required structured JSON output - no prose, no markdown, no explanation \
outside the JSON."""


SEMANTIC_DUPLICATE_SYSTEM_PROMPT = """You are a strict bilingual Arabic/English interview-question duplicate classifier.
For each supplied pair, return exactly one classification:
- DUPLICATE: both questions seek substantially the same answer or reuse the same interview intent, even if paraphrased.
- SAME_TOPIC_DIFFERENT_ANGLE: they share a subject but seek materially different answers (for example origin vs implementation challenge).
- DIFFERENT: their subjects and purposes differ.

Judge intent, not mere shared topic words. Be conservative about DUPLICATE, but detect clear Arabic and English paraphrases. Use the short intent summaries as semantic labels when present. Return only the strict JSON schema. Do not provide reasoning, prose, tools, browsing, or chain-of-thought."""


def build_user_prompt(
    guest: Guest,
    research_items: list[ResearchContextItem],
    options: QuestionGenerationOptions,
    existing_questions: list[ExistingQuestionItem] | None = None,
) -> str:
    lines = [
        "GUEST METADATA (application-provided profile data):",
        f"- name: {guest.name}",
        f"- job_title: {guest.job_title or 'unknown'}",
        f"- company: {guest.company or 'unknown'}",
        "",
        "RESEARCH CONTEXT (the ONLY evidence you may use - already extracted and verified, "
        "each item citable by its ID):",
    ]

    if not research_items:
        lines.append(
            "(no research items are available for this guest - rely only on guest metadata "
            "above, and leave research_item_ids empty for every question)"
        )
    else:
        for item in research_items:
            lines.append(f"[{item.id}] ({item.item_type})")
            lines.append(item.fact)
            lines.append("")

    lines.extend(
        [
            "",
            "EXISTING QUESTIONS TO AVOID (saved manual and AI questions; do not repeat or "
            "paraphrase their intent):",
        ]
    )
    if not existing_questions:
        lines.append("(none)")
    else:
        for item in existing_questions:
            details = [f"[{item.id}] {item.text}"]
            if item.topic:
                details.append(f"topic={item.topic}")
            if item.intent_summary:
                details.append(f"covered_intent={item.intent_summary}")
            lines.append(" | ".join(details))

    covered_intents = [
        (item.id, item.intent_summary)
        for item in (existing_questions or [])
        if item.intent_summary
    ]
    lines.extend(["", "PREVIOUSLY COVERED INTERVIEW INTENTS/ANGLES:"])
    if covered_intents:
        lines.extend(f"- [{item_id}] {intent}" for item_id, intent in covered_intents)
    else:
        lines.append("(none stored yet; infer covered purposes from the existing question text)")

    language_label = "Arabic" if options.language == "ar" else "English"
    lines.extend(
        [
            "",
            "GENERATION REQUEST:",
            f"- requested question count: {options.count}",
            f"- output language: {language_label}",
            f"- style: {options.style}",
            f"- include follow-up questions: {options.include_followups}",
        ]
    )
    if options.topics:
        lines.append(
            "- focus on these topics where the research supports it: " + ", ".join(options.topics)
        )

    lines.append(
        "\nGenerate personalized, source-grounded interview questions about this guest "
        "following every rule in the system instructions. Cite research IDs exactly as given "
        "above (e.g. R1, R3) for every question that references a specific fact."
    )
    return "\n".join(lines)


def build_semantic_duplicate_prompt(pairs: list[SemanticComparisonPair]) -> str:
    lines = [
        "Classify each comparison independently. A later candidate may duplicate an earlier "
        "candidate. Return one decision for every pair_id.",
        "",
    ]
    for pair in pairs:
        candidate = pair.candidate
        reference = pair.reference
        lines.extend(
            [
                f"PAIR {pair.id}",
                f"candidate_text: {candidate.text}",
                f"candidate_topic: {candidate.topic or 'unknown'}",
                f"candidate_intent: {candidate.intent_summary or 'unknown'}",
                f"reference_text: {reference.text}",
                f"reference_topic: {reference.topic or 'unknown'}",
                f"reference_intent: {reference.intent_summary or 'unknown'}",
                "",
            ]
        )
    return "\n".join(lines)
