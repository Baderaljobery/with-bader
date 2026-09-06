import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from groq import APIConnectionError, APIError, APITimeoutError

from app.audio.base import STTProviderError, STTTimeoutError
from app.audio.models import AudioInput, TranscriptionOptions
from app.audio.providers.groq import GroqWhisperSTTProvider


def _audio(content: bytes = b"fake-audio-bytes") -> AudioInput:
    return AudioInput(filename="clip.mp3", content_type="audio/mpeg", content=content, size_bytes=len(content))


def _fake_response(text: str):
    response = MagicMock()
    response.text = text
    return response


def _patch_transcriptions_create(return_value=None, side_effect=None):
    mock_create = AsyncMock(return_value=return_value, side_effect=side_effect)
    mock_client = MagicMock()
    mock_client.audio.transcriptions.create = mock_create
    return patch("app.audio.providers.groq.AsyncGroq", return_value=mock_client), mock_create


class GroqWhisperSTTProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_transcription_returns_text(self):
        patcher, mock_create = _patch_transcriptions_create(return_value=_fake_response("مرحبا بالجميع"))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3")
            result = await provider.transcribe(_audio())

        self.assertEqual(result.text, "مرحبا بالجميع")
        self.assertEqual(result.provider, "groq")
        self.assertEqual(result.model, "whisper-large-v3")

    async def test_defaults_to_arabic_when_no_options_given(self):
        patcher, mock_create = _patch_transcriptions_create(return_value=_fake_response("hi"))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3", default_language="ar")
            result = await provider.transcribe(_audio())

        self.assertEqual(mock_create.call_args.kwargs["language"], "ar")
        self.assertEqual(result.language, "ar")

    async def test_explicit_options_language_overrides_default(self):
        patcher, mock_create = _patch_transcriptions_create(return_value=_fake_response("hi"))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3", default_language="ar")
            result = await provider.transcribe(_audio(), TranscriptionOptions(language="en"))

        self.assertEqual(mock_create.call_args.kwargs["language"], "en")
        self.assertEqual(result.language, "en")

    async def test_uses_configured_model(self):
        patcher, mock_create = _patch_transcriptions_create(return_value=_fake_response(""))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3-turbo")
            await provider.transcribe(_audio())

        self.assertEqual(mock_create.call_args.kwargs["model"], "whisper-large-v3-turbo")

    async def test_sends_file_as_filename_bytes_content_type_tuple(self):
        patcher, mock_create = _patch_transcriptions_create(return_value=_fake_response(""))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3")
            await provider.transcribe(_audio(content=b"real-bytes"))

        filename, content, content_type = mock_create.call_args.kwargs["file"]
        self.assertEqual(filename, "clip.mp3")
        self.assertEqual(content, b"real-bytes")
        self.assertEqual(content_type, "audio/mpeg")

    async def test_timeout_maps_to_timeout_error(self):
        patcher, _ = _patch_transcriptions_create(side_effect=APITimeoutError(request=MagicMock()))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3")
            with self.assertRaises(STTTimeoutError):
                await provider.transcribe(_audio())

    async def test_connection_error_maps_to_provider_error(self):
        patcher, _ = _patch_transcriptions_create(side_effect=APIConnectionError(request=MagicMock()))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3")
            with self.assertRaises(STTProviderError):
                await provider.transcribe(_audio())

    async def test_api_error_maps_to_provider_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 429
        exc = APIError(message="rate limited", request=MagicMock(), body=None)
        exc.status_code = 429
        patcher, _ = _patch_transcriptions_create(side_effect=exc)
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="fake-key", model="whisper-large-v3")
            with self.assertRaises(STTProviderError):
                await provider.transcribe(_audio())

    async def test_never_leaks_api_key_in_result(self):
        patcher, _ = _patch_transcriptions_create(return_value=_fake_response("some text"))
        with patcher:
            provider = GroqWhisperSTTProvider(api_key="super-secret-key", model="whisper-large-v3")
            result = await provider.transcribe(_audio())

        self.assertNotIn("super-secret-key", result.text)
        self.assertNotIn("super-secret-key", str(result.metadata))


if __name__ == "__main__":
    unittest.main()
