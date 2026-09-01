import unittest

from app.audio.base import SpeechToTextProvider
from app.audio.models import (
    AudioInput,
    TranscriptionOptions,
    TranscriptionResult,
    TranscriptionSegment,
)
from app.audio.service import SpeechToTextService


class _FakeProvider(SpeechToTextProvider):
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, result: TranscriptionResult):
        self._result = result
        self.received_audio = None
        self.received_options = None

    async def transcribe(self, audio, options=None):
        self.received_audio = audio
        self.received_options = options
        return self._result


def _audio() -> AudioInput:
    return AudioInput(filename="a.mp3", content_type="audio/mpeg", content=b"x", size_bytes=1)


class SpeechToTextServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_service_delegates_to_provider(self):
        expected = TranscriptionResult(text="hello", provider="fake", model="fake-model")
        provider = _FakeProvider(expected)
        service = SpeechToTextService(provider=provider)

        result = await service.transcribe(_audio())

        self.assertIs(result, expected)

    async def test_service_passes_audio_and_options_through_unchanged(self):
        provider = _FakeProvider(TranscriptionResult(text="", provider="fake", model="fake-model"))
        service = SpeechToTextService(provider=provider)
        audio = _audio()
        options = TranscriptionOptions(language="en", prompt="context")

        await service.transcribe(audio, options)

        self.assertIs(provider.received_audio, audio)
        self.assertIs(provider.received_options, options)

    async def test_future_optional_segment_model_works_without_provider_changes(self):
        """Proves the normalized contract already supports a richer future
        provider (e.g. with diarization/timestamps) without any code change
        to SpeechToTextService or the Cohere implementation."""
        rich_result = TranscriptionResult(
            text="Hello there, how are you?",
            language="en",
            duration_seconds=12.5,
            provider="future-provider",
            model="future-model",
            segments=[
                TranscriptionSegment(start=0.0, end=1.2, text="Hello there,", speaker="speaker_1"),
                TranscriptionSegment(start=1.2, end=2.5, text="how are you?", speaker="speaker_2"),
            ],
            metadata={"confidence": 0.97},
        )
        provider = _FakeProvider(rich_result)
        service = SpeechToTextService(provider=provider)

        result = await service.transcribe(_audio())

        self.assertEqual(len(result.segments), 2)
        self.assertEqual(result.segments[0].speaker, "speaker_1")
        self.assertEqual(result.duration_seconds, 12.5)


if __name__ == "__main__":
    unittest.main()
