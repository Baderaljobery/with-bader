from app.audio.base import SpeechToTextProvider
from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult


class SpeechToTextService:
    """Provider-independent entry point for all STT consumers.

    Today: the General Text Extract tool (app/api/text_extract.py).
    Later: the Guest Interview workspace will call this exact same service
    (`result = await speech_to_text_service.transcribe(audio)`) and pass
    `result.text` into a future InterviewIntelligenceService for question
    matching/answer extraction - not implemented in this phase.

    Callers must depend on this service (or the AudioInput/
    TranscriptionResult models), never on a concrete provider directly.
    """

    def __init__(self, provider: SpeechToTextProvider) -> None:
        self.provider = provider

    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        return await self.provider.transcribe(audio, options)


def get_speech_to_text_service() -> SpeechToTextService:
    """Single wiring point for the provider implementation. Swap via
    STT_PROVIDER - SpeechToTextService itself never changes."""
    from app.audio.factory import build_stt_provider

    return SpeechToTextService(provider=build_stt_provider())
