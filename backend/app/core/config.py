from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str

    research_max_queries: int = 8
    research_results_per_query: int = 5

    research_search_provider: str = "mock"
    research_fallback_provider: str | None = None
    research_search_timeout_seconds: float = 15.0
    research_source_content_max_chars: int = 2000
    tavily_api_key: str | None = None
    exa_api_key: str | None = None

    research_extractor_provider: str = "mock"
    # Kept modest by default so a single extraction request comfortably fits
    # within Groq's free/on-demand tier tokens-per-minute budget (8000 TPM
    # for openai/gpt-oss-20b as observed) alongside the system prompt and
    # JSON schema overhead. Raise these if using a higher Groq tier.
    research_extractor_max_sources: int = 8
    research_extractor_max_source_chars: int = 700

    groq_api_key: str | None = None
    groq_research_model: str = "openai/gpt-oss-20b"
    groq_timeout_seconds: float = 30.0
    groq_max_output_tokens: int = 1800
    groq_reasoning_effort: str = "low"

    question_generator_provider: str = "mock"
    groq_question_model: str = "openai/gpt-oss-20b"
    question_generation_default_count: int = 12
    question_generation_max_count: int = 20
    question_generation_max_research_items: int = 30
    question_generation_max_input_chars: int = 12000

    question_improver_provider: str = "mock"
    groq_question_improvement_model: str = "openai/gpt-oss-20b"

    stt_provider: str = "cohere"
    stt_max_file_size_mb: int = 25
    stt_timeout_seconds: float = 60.0
    # Comma-separated override, e.g. ".mp3,.wav". Falls back to a built-in
    # default list (see app/audio/validation.py) when unset.
    stt_allowed_extensions: str | None = None

    cohere_api_key: str | None = None
    cohere_stt_model: str = "cohere-transcribe-arabic-07-2026"

    interview_matcher_provider: str = "mock"
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
    groq_content_model: str = "openai/gpt-oss-20b"
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

    openrouter_api_key: str | None = None
    # "Nano Banana 2" (Gemini 3.1 Flash Image), Google's current fast,
    # general-purpose native image model, called through OpenRouter rather
    # than Google's own API directly - Google Cloud's Gemini API free tier
    # allocates zero quota for image-output models, while OpenRouter bills
    # per-request against its own credit balance instead.
    openrouter_image_model: str = "google/gemini-3.1-flash-image"
    openrouter_timeout_seconds: float = 60.0
    design_generation_max_body_chars: int = 600
    design_generation_max_questions: int = 6

    slide_planner_provider: str = "mock"
    groq_slide_planner_model: str = "openai/gpt-oss-20b"


settings = Settings()
