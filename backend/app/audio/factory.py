from app.audio.base import SpeechToTextProvider, STTProviderConfigurationError
from app.core.config import settings


def build_stt_provider() -> SpeechToTextProvider:
    """Resolve the configured STT provider.

    STT_PROVIDER: "groq" (default). Unsupported value - or "groq" without
    GROQ_API_KEY configured - fails clearly rather than silently doing
    nothing, matching how the LLM provider factories in this project handle
    the same situation. Reuses the same GROQ_API_KEY every other Groq
    feature in this project uses - no separate STT-only key.
    """
    provider = (settings.stt_provider or "groq").strip().lower()

    if provider == "groq":
        if not settings.groq_api_key:
            raise STTProviderConfigurationError(
                "Provider 'groq' requires GROQ_API_KEY, which is not configured"
            )
        from app.audio.providers.groq import GroqWhisperSTTProvider

        return GroqWhisperSTTProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_stt_model,
            timeout_seconds=settings.stt_timeout_seconds,
            default_language=settings.groq_stt_language,
        )

    raise STTProviderConfigurationError(
        f"Unknown STT provider '{provider}' (supported: groq)"
    )
