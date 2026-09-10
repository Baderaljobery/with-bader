from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    environment: str = "development"

    # Comma-separated so operators can configure this without JSON quoting.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Authentication ---
    # HS256-signed session token stored as an HttpOnly cookie (see
    # app/core/security.py, app/core/auth.py) - no session table, no
    # localStorage/sessionStorage token exposure to browser JS.
    auth_secret: str
    auth_cookie_name: str = "with_bader_session"
    # 14 days - a workspace tool a user opens daily shouldn't demand a
    # fresh login on every visit; refreshing the page must never log the
    # user out (Part 50 of the auth rework spec).
    auth_token_expire_minutes: int = 60 * 24 * 14
    registration_mode: Literal["open", "closed"] = "open"

    # Sliding-window rate limits. The application is intentionally deployed
    # as one API process on one server, so an in-process store is sufficient
    # and avoids adding Redis solely for throttling.
    login_rate_limit: int = Field(default=10, ge=1)
    login_rate_window_seconds: int = Field(default=60, ge=1)
    register_rate_limit: int = Field(default=5, ge=1)
    register_rate_window_seconds: int = Field(default=3600, ge=1)
    ai_rate_limit: int = Field(default=30, ge=1)
    ai_rate_window_seconds: int = Field(default=60, ge=1)

    # Adaptive search budget (Phase 10): research_max_queries is now the hard
    # ceiling a single run will never exceed regardless of guest profile
    # richness; research_min_queries is the floor for a very thin profile.
    # app/research/collectors/query_builder.py.estimate_query_budget picks
    # the actual per-guest budget between the two. Raised from the previous
    # flat 8 to accommodate a genuinely richer, bilingual guest.
    research_max_queries: int = 16
    research_min_queries: int = 6
    research_results_per_query: int = 5

    # Hybrid research planner (Phase 8): the deterministic queries
    # (query_builder.py) always run; this only toggles the bounded
    # AI-assisted query expansion on top of them (app/research/research_planner.py).
    # Off entirely (e.g. in tests) leaves the deterministic-only behavior.
    research_planner_enabled: bool = True

    research_search_provider: str = "mock"
    research_fallback_provider: str | None = None
    research_search_timeout_seconds: float = 15.0
    research_source_content_max_chars: int = 2000
    tavily_api_key: str | None = None
    exa_api_key: str | None = None

    # Quality-based Tavily fallback (Phase 14): beyond the existing
    # exception-triggered per-query fallback (app/research/providers/fallback.py,
    # unchanged), ResearchEngine issues a small supplementary batch of the
    # weakest-covered queries directly to the fallback provider when the
    # PRIMARY provider's aggregate results look weak - see
    # app/research/research_engine.py._needs_quality_fallback.
    research_quality_fallback_min_sources: int = 4
    research_quality_fallback_min_domains: int = 3
    research_quality_fallback_max_queries: int = 4

    # Identity resolution (Phase 11): a source below this relevance score
    # (0-1, app/research/identity_resolution.py) is treated as low-confidence
    # and excluded before ranking/extraction - it is not deleted, just not
    # trusted as evidence about this specific guest.
    research_identity_min_relevance: float = 0.2
    # Below this AGGREGATE relevance across all evidence, the run is
    # reported as needing identity confirmation rather than producing a
    # confident-looking profile from weak evidence.
    research_identity_confirmation_threshold: float = 0.35

    # Trusted-link retrieval (Phase 12) - see
    # app/research/collectors/link_content_fetcher.py. Deliberately
    # conservative: public http/https only, small size/time budget, no
    # redirect chains long enough to be useful for SSRF probing.
    research_link_fetch_enabled: bool = True
    research_link_fetch_timeout_seconds: float = 8.0
    research_link_fetch_max_bytes: int = 1_500_000
    research_link_fetch_max_redirects: int = 3
    research_link_fetch_max_text_chars: int = 4000

    research_extractor_provider: str = "mock"
    # Kept modest by default so a single extraction request comfortably fits
    # within Groq's free/on-demand tier tokens-per-minute budget (8000 TPM
    # for openai/gpt-oss-20b as observed) alongside the system prompt and
    # JSON schema overhead. Raise these if using a higher Groq tier.
    # Evidence budget (Phase 17): "max_sources" is now Stage B's (richer
    # per-source evidence) limit; Stage A (cheap candidate evaluation - see
    # app/research/extraction/source_selector.py) considers every
    # deduplicated source before narrowing down to this many.
    research_extractor_max_sources: int = 8
    research_extractor_max_source_chars: int = 700

    groq_api_key: str | None = None
    groq_research_model: str = "openai/gpt-oss-120b"
    groq_timeout_seconds: float = 30.0
    # Raised from 1800 (2026-09-06, paid-tier upgrade): the reasoning_effort
    # bump below spends part of this same budget on hidden reasoning tokens
    # before the model even starts the visible JSON answer, and the larger
    # 120b models now used by most Groq features produce richer output -
    # both narrow the previous headroom. 3000 restores comfortable headroom
    # now that a paid tier's TPM budget is no longer the constraint the old
    # 1800 value was sized for.
    groq_max_output_tokens: int = 3000
    # "low" -> "medium" (2026-09-06): only app/research/extraction/groq.py
    # currently reads this setting - no other Groq provider class accepts a
    # reasoning_effort parameter, so this only changes research extraction's
    # behavior today.
    groq_reasoning_effort: str = "medium"

    question_generator_provider: str = "mock"
    groq_question_model: str = "openai/gpt-oss-120b"
    question_generation_default_count: int = 12
    question_generation_max_count: int = 20
    question_generation_max_research_items: int = 30
    question_generation_max_input_chars: int = 12000
    # Generate a bounded surplus, then remove historical/intra-batch semantic
    # duplicates and select a diverse final set. One refill keeps cost bounded.
    question_generation_candidate_multiplier: float = Field(default=1.5, ge=1.0, le=3.0)
    question_generation_max_candidates: int = Field(default=30, ge=1, le=60)
    question_generation_max_refill_attempts: int = Field(default=1, ge=0, le=2)
    question_generation_max_existing_questions: int = Field(default=500, ge=1, le=2000)
    question_generation_max_existing_prompt_questions: int = Field(default=50, ge=1, le=500)
    question_generation_max_semantic_pairs: int = Field(default=80, ge=1, le=300)
    question_generation_lexical_duplicate_threshold: float = Field(
        default=0.88, ge=0.5, le=1.0
    )
    question_generation_intent_duplicate_threshold: float = Field(
        default=0.82, ge=0.5, le=1.0
    )
    question_generation_semantic_candidate_threshold: float = Field(
        default=0.12, ge=0.0, le=1.0
    )

    question_improver_provider: str = "mock"
    groq_question_improvement_model: str = "openai/gpt-oss-120b"

    stt_provider: str = "groq"
    # Overall/absolute cap on what the app will even attempt to process
    # (2026-09-06, Groq Whisper migration) - distinct from
    # stt_direct_max_bytes below. A file under this but over the direct
    # limit is automatically chunked (see app/audio/service.py); a file
    # over this is rejected outright. 500MB of speech-oriented mono/16kHz
    # audio is many hours long - comfortably beyond any real interview.
    stt_max_file_size_mb: int = 500
    stt_timeout_seconds: float = 60.0
    # Comma-separated override, e.g. ".mp3,.wav". Falls back to a built-in
    # default list (see app/audio/validation.py) when unset.
    stt_allowed_extensions: str | None = None

    # Verified against Groq's official docs (console.groq.com/docs/
    # speech-to-text) on 2026-09-06: 25MB on the free tier, 100MB on a
    # paid/dev tier - this project has a paid key, so 100MB is the direct-
    # upload threshold. A file at or under this goes straight to Groq; a
    # larger one is chunked first (see app/audio/chunking.py). Configurable
    # in case Groq's own limit changes or the account tier changes.
    stt_direct_max_bytes: int = 100 * 1024 * 1024
    # Time-based chunk length for files over stt_direct_max_bytes. 15
    # minutes keeps each chunk comfortably under the direct limit even for
    # higher-bitrate source audio, without creating dozens of tiny chunks
    # for a typical hour-long interview (~4 chunks).
    stt_chunk_minutes: int = 15

    groq_stt_model: str = "whisper-large-v3"
    # This app transcribes Arabic interviews - always pass language
    # explicitly rather than relying on Whisper's auto-detection (see
    # app/audio/providers/groq.py).
    groq_stt_language: str = "ar"

    interview_matcher_provider: str = "mock"
    # Deliberately kept on the smaller model (2026-09-06 review): this is a
    # bounded, strict-JSON-schema matching task over a fixed question list,
    # not open-ended generation - low temperature (0.2), no reasoning_effort
    # even wired in. No evidence surfaced that 20b's quality is the limiting
    # factor here, so it wasn't upgraded alongside the generation/planning
    # features.
    groq_interview_matcher_model: str = "openai/gpt-oss-20b"
    # Deliberately lower than a naive "30000" default: empirically, Groq's
    # free/on-demand tier enforces an ~8000 tokens-per-minute budget for
    # openai/gpt-oss-20b (see the research-extraction task's 413 finding).
    # A 30000-character transcript alone is already ~7500 tokens, which
    # would blow that budget before accounting for the system prompt,
    # question list, schema, and output. This default is sized to leave
    # headroom for a typical (5-15 question) run; raise it on a paid tier.
    interview_matcher_max_transcript_chars: int = 12000
    interview_matcher_max_questions: int = 50
    interview_matcher_auto_save_confidence: float = 0.75

    content_generator_provider: str = "mock"
    groq_content_model: str = "openai/gpt-oss-120b"
    # Context-building limits, same spirit as question_generation's - keep a
    # single generation request comfortably within Groq's tokens-per-minute
    # budget. The transcript gets its own (smaller) cap since it is only
    # supporting evidence, never the primary source (see PART on transcript
    # context in the content-creation spec).
    content_generation_max_answers: int = 12
    content_generation_max_notebook_blocks: int = 15
    content_generation_max_research_items: int = 10
    content_generation_max_questions: int = 8
    content_generation_max_transcript_chars: int = 4000
    content_generation_max_input_chars: int = 10000

    slide_planner_provider: str = "mock"
    groq_slide_planner_model: str = "openai/gpt-oss-120b"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
