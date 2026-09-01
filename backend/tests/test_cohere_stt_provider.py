import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import cohere
import httpx

from app.audio.base import STTProviderError, STTTimeoutError
from app.audio.models import AudioInput, TranscriptionOptions
from app.audio.providers.cohere import CohereSTTProvider


def _audio(filename="clip.mp3", content_type="audio/mpeg", data=b"fake-audio-bytes") -> AudioInput:
    return AudioInput(
        filename=filename, content_type=content_type, content=data, size_bytes=len(data)
    )


def _patch_create(side_effect=None, return_value=None):
    mock_create = AsyncMock(side_effect=side_effect, return_value=return_value)
    fake_client = MagicMock()
    fake_client.audio = MagicMock()
    fake_client.audio.transcriptions = MagicMock()
    fake_client.audio.transcriptions.create = mock_create
    return patch(
        "app.audio.providers.cohere.cohere.AsyncClient", return_value=fake_client
    ), mock_create


class CohereSTTProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_transcription_normalized(self):
        response = MagicMock(text="مرحبا بكم في هذا المقطع الصوتي")
        patcher, mock_create = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="cohere-transcribe-arabic-07-2026")
            result = await provider.transcribe(_audio())

        self.assertEqual(result.text, "مرحبا بكم في هذا المقطع الصوتي")
        self.assertEqual(result.provider, "cohere")
        self.assertEqual(result.model, "cohere-transcribe-arabic-07-2026")

    async def test_normalized_missing_fields_remain_null(self):
        response = MagicMock(text="hello")
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            result = await provider.transcribe(_audio())

        # language is "ar" because the application knows the request
        # explicitly asked Cohere for Arabic - not fabricated, not echoed
        # back by Cohere (whose response only ever contains `text`).
        self.assertEqual(result.language, "ar")
        self.assertIsNone(result.duration_seconds)
        self.assertIsNone(result.segments)
        self.assertIsNone(result.metadata)

    async def test_provider_and_model_surfaced(self):
        response = MagicMock(text="hello")
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="cohere-transcribe-arabic-07-2026")
            result = await provider.transcribe(_audio())

        self.assertEqual(result.provider, "cohere")
        self.assertEqual(result.model, "cohere-transcribe-arabic-07-2026")

    async def test_raw_cohere_response_not_surfaced(self):
        response = MagicMock(text="hello")
        response.some_internal_cohere_field = "should never leak"
        patcher, _ = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            result = await provider.transcribe(_audio())

        self.assertFalse(hasattr(result, "some_internal_cohere_field"))
        dumped = result.model_dump()
        self.assertNotIn("some_internal_cohere_field", dumped)
        self.assertEqual(set(dumped.keys()), {
            "text", "language", "duration_seconds", "provider", "model", "segments", "metadata"
        })

    async def test_network_timeout_mapped_to_stt_timeout_error(self):
        request = httpx.Request("POST", "https://api.cohere.com/v2/audio/transcriptions")
        patcher, _ = _patch_create(side_effect=httpx.ReadTimeout("timed out", request=request))
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            with self.assertRaises(STTTimeoutError):
                await provider.transcribe(_audio())

    async def test_cohere_gateway_timeout_mapped_to_stt_timeout_error(self):
        error = cohere.GatewayTimeoutError(body={"message": "gateway timeout"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            with self.assertRaises(STTTimeoutError):
                await provider.transcribe(_audio())

    async def test_cohere_api_error_mapped_to_provider_error(self):
        error = cohere.InternalServerError(body={"message": "server exploded"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            with self.assertRaises(STTProviderError):
                await provider.transcribe(_audio())

    async def test_provider_error_does_not_leak_raw_body(self):
        error = cohere.BadRequestError(body={"message": "secret internal detail xyz"})
        patcher, _ = _patch_create(side_effect=error)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            try:
                await provider.transcribe(_audio())
                self.fail("expected STTProviderError")
            except STTProviderError as exc:
                self.assertNotIn("secret internal detail xyz", str(exc))

    async def test_always_sends_arabic_when_no_options_given(self):
        response = MagicMock(text="hello")
        patcher, mock_create = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            await provider.transcribe(_audio(), options=None)

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["language"], "ar")

    async def test_always_sends_arabic_even_if_caller_requests_another_language(self):
        """A caller cannot accidentally (or deliberately) cause Cohere to
        receive anything other than "ar" - this is a Cohere-provider
        decision, not something TranscriptionOptions.language controls."""
        response = MagicMock(text="hello")
        patcher, mock_create = _patch_create(return_value=response)
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            await provider.transcribe(_audio(), options=TranscriptionOptions(language="en"))

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["language"], "ar")

    async def test_file_sent_as_filename_bytes_content_type_tuple(self):
        response = MagicMock(text="hello")
        patcher, mock_create = _patch_create(return_value=response)
        audio = _audio(filename="interview.wav", content_type="audio/wav", data=b"raw-bytes")
        with patcher:
            provider = CohereSTTProvider(api_key="fake-key", model="test-model")
            await provider.transcribe(audio)

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["file"], ("interview.wav", b"raw-bytes", "audio/wav"))


if __name__ == "__main__":
    unittest.main()
