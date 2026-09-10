import hashlib
import re
import unicodedata


_ARABIC_DIACRITICS_RE = re.compile(
    "[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]"
)
_ARABIC_ALEF_RE = re.compile("[\u0622\u0623\u0625\u0671]")

# Question glue words add a lot of accidental overlap while saying little
# about the subject or interview intent. This deliberately small bilingual
# list is used for similarity only; it never changes stored/displayed text.
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "did",
    "do",
    "does",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "which",
    "why",
    "with",
    "you",
    "your",
    "أن",
    "او",
    "أي",
    "إلى",
    "الى",
    "التي",
    "الذي",
    "الذين",
    "عن",
    "على",
    "في",
    "كان",
    "كانت",
    "كيف",
    "ما",
    "ماذا",
    "ماهي",
    "ماهو",
    "ماهي",
    "ماهو",
    "من",
    "هل",
    "هو",
    "هي",
    "و",
}


def normalize_question_text(value: str) -> str:
    """Conservatively normalize Arabic/Latin question text.

    This is intentionally suitable for equality/fingerprinting, not display:
    Unicode compatibility forms, Arabic marks/tatweel, punctuation and spacing
    are normalized while letters that can change meaning remain untouched.
    """
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = _ARABIC_DIACRITICS_RE.sub("", value).replace("\u0640", "")
    value = _ARABIC_ALEF_RE.sub("ا", value).replace("ى", "ي")
    chars = []
    for char in value:
        category = unicodedata.category(char)
        chars.append(" " if category.startswith("P") else char)
    return " ".join("".join(chars).split())


def normalized_question_hash(value: str) -> str:
    return hashlib.sha256(normalize_question_text(value).encode("utf-8")).hexdigest()


def _light_token_form(token: str) -> str:
    # Conservative Arabic conjunction/preposition normalization for lexical
    # candidate discovery. Exact matching always uses the unstripped form.
    for prefix in ("وال", "بال", "كال", "فال", "لل"):
        if token.startswith(prefix) and len(token) - len(prefix) >= 3:
            return token[len(prefix) :]
    if token.startswith("ال") and len(token) > 5:
        return token[2:]
    return token


def meaningful_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    for raw in normalize_question_text(value).split():
        if raw in _STOP_WORDS or len(raw) <= 1:
            continue
        tokens.add(_light_token_form(raw))
    return tokens


def lexical_similarity(left: str, right: str) -> float:
    """Cheap lexical signal combining Jaccard and smaller-side containment."""
    a = meaningful_tokens(left)
    b = meaningful_tokens(right)
    if not a or not b:
        return 0.0
    intersection = len(a & b)
    jaccard = intersection / len(a | b)
    containment = intersection / min(len(a), len(b))
    return max(jaccard, containment * 0.85)


def same_optional_label(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return normalize_question_text(left) == normalize_question_text(right)
