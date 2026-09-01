from app.audio.base import SpeechToTextProvider, STTProviderConfigurationError
from app.core.config import settings


def build_stt_provider() -> SpeechToTextProvider:
    """Resolve the configured STT provider.

    STT_PROVIDER: "cohere" (default). Unsupported value - or "cohere"
    without COHERE_API_KEY configured - fails clearly rather than silently
    doing nothing, matching how the LLM provider factories in this project
    handle the same situation.
    """
    provider = (settings.stt_provider or "cohere").strip().lower()

    if provider == "cohere":
        if not settings.cohere_api_key:
            raise STTProviderConfigurationError(
                "Provider 'cohere' requires COHERE_API_KEY, which is not configured"
            )
        from app.audio.providers.cohere import CohereSTTProvider

        return CohereSTTProvider(
            api_key=settings.cohere_api_key,
            model=settings.cohere_stt_model,
            timeout_seconds=settings.stt_timeout_seconds,
        )

    raise STTProviderConfigurationError(
        f"Unknown STT provider '{provider}' (supported: cohere)"
    )
