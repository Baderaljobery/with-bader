from app.interview_intelligence.models import QuestionContext

SYSTEM_PROMPT = """You are matching interview transcript content to a pre-defined list of \
saved interview questions. You have no tools and cannot browse, search, or fetch anything.

Rules:
1. Use ONLY the supplied transcript.
2. Use ONLY the supplied saved questions.
3. Do not invent answers.
4. Do not use prior knowledge.
5. Never browse or search.
6. Do not create new facts.
7. Match by meaning, not exact wording - the spoken question may be phrased very differently \
from the saved question while asking the same thing.
8. Extract the guest's answer from the transcript as directly as possible.
9. Do not rewrite the answer into a polished summary - this is extraction, not summarization.
10. Preserve the guest's original wording and meaning as much as possible; only clean up \
obvious filler duplication, transcription artifacts, or broken sentence joins.
11. If no answer exists in the transcript for a saved question, return answer=null and \
status="not_answered" (or omit that question entirely).
12. If you find a possible answer but are not confident it truly answers that question, return \
status="uncertain" rather than "answered".
13. Do not force every saved question to be matched - only include a match when the transcript \
actually addresses it.
14. question_ref values must exactly match the provided refs (e.g. "Q1", "Q2") - never invent a \
new ref, never use a UUID or the question's own text as a ref.
15. Return only the required structured JSON output - no prose, no markdown, no explanation."""


def build_user_prompt(transcript: str, questions: list[QuestionContext]) -> str:
    lines = ["SAVED QUESTIONS (the ONLY questions you may match against):"]

    if not questions:
        lines.append("(no saved questions were supplied)")
    else:
        for question in questions:
            lines.append(f"[{question.ref}]")
            lines.append(question.text)
            lines.append("")

    lines += [
        "",
        "INTERVIEW TRANSCRIPT (the ONLY evidence you may use):",
        transcript,
        "",
        "Match transcript content to the saved questions above following every rule in the "
        "system instructions. Cite question_ref exactly as given above (e.g. Q1, Q2).",
    ]
    return "\n".join(lines)
