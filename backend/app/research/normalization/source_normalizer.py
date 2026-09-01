from urllib.parse import urlsplit, urlunsplit

from app.research.models import NormalizedResearchSource, RawResearchSource

KNOWN_SOURCE_TYPES = {
    "linkedin",
    "website",
    "company_website",
    "article",
    "interview",
    "youtube",
    "x",
    "news",
    "uploaded_document",
    "other",
}

_SOURCE_TYPE_ALIASES = {
    "twitter": "x",
}

_DOMAIN_TYPE_RULES = (
    ("linkedin.com", "linkedin"),
    ("youtube.com", "youtube"),
    ("youtu.be", "youtube"),
    ("twitter.com", "x"),
    ("x.com", "x"),
)

_NEWS_DOMAIN_HINTS = (
    "news",
    "reuters.com",
    "bloomberg.com",
    "forbes.com",
    "techcrunch.com",
    "bbc.",
    "cnn.com",
    "nytimes.com",
)


def _clean_str(value: str | None) -> str | None:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def _normalize_source_type(source_type: str | None) -> str:
    if not source_type:
        return "other"
    normalized = source_type.strip().lower().replace(" ", "_")
    normalized = _SOURCE_TYPE_ALIASES.get(normalized, normalized)
    return normalized if normalized in KNOWN_SOURCE_TYPES else "other"


def _canonicalize_url(url: str | None) -> str | None:
    url = _clean_str(url)
    if not url:
        return None
    parts = urlsplit(url)
    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[len("www.") :]
    path = parts.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))


def infer_source_type_from_url(url: str | None) -> str:
    """Simple, deterministic domain-based source-type guess for search results
    that don't otherwise carry a source_type. Deliberately small - a handful
    of well-known domains plus a coarse "news" hint, defaulting to "website"."""
    if not url:
        return "other"
    host = urlsplit(url).netloc.lower()
    if host.startswith("www."):
        host = host[len("www.") :]
    if not host:
        return "other"
    for domain, source_type in _DOMAIN_TYPE_RULES:
        if host == domain or host.endswith(f".{domain}"):
            return source_type
    if any(hint in host for hint in _NEWS_DOMAIN_HINTS):
        return "news"
    return "website"


def normalize_source(raw: RawResearchSource) -> NormalizedResearchSource:
    return NormalizedResearchSource(
        source_type=_normalize_source_type(raw.source_type),
        url=_clean_str(raw.url),
        canonical_url=_canonicalize_url(raw.url),
        title=_clean_str(raw.title),
        publisher=_clean_str(raw.publisher),
        published_at=raw.published_at,
        content=_clean_str(raw.content),
        snippet=_clean_str(raw.snippet),
        metadata=raw.metadata or {},
    )


def normalize_sources(raw_sources: list[RawResearchSource]) -> list[NormalizedResearchSource]:
    return [normalize_source(raw) for raw in raw_sources]
