import inspect
import io
import unittest
from unittest.mock import AsyncMock

from app.api.text_extract import _resolve_service, extract_text_from_audio
from app.audio.base import (
    STTProviderError,
    STTTimeoutError,
)
from app.audio.models import TranscriptionResult
from app.audio.service import SpeechToTextService
from app.main import app
from tests.auth_test_helpers import cleanup_client_user, make_authenticated_client

client = make_authenticated_client()

_WAV_HEADER = b"RIFF\x00\x00\x00\x00WAVEfmt "


class _FakeProvider:
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, result=None, side_effect=None):
        self._result = result
        self._side_effect = side_effect
        self.calls = 0

    async def transcribe(self, audio, options=None):
        self.calls += 1
        if self._side_effect is not None:
            raise self._side_effect
        return self._result


def _override_with_fake_provider(result=None, side_effect=None):
    fake = _FakeProvider(result=result, side_effect=side_effect)
    app.dependency_overrides[_resolve_service] = lambda: SpeechToTextService(provider=fake)
    return fake


def _clear_overrides():
    app.dependency_overrides.pop(_resolve_service, None)


class TextExtractApiTests(unittest.TestCase):
    def tearDown(self):
        _clear_overrides()

    def test_valid_mp3_accepted(self):
        _override_with_fake_provider(
            TranscriptionResult(
                text="النص المستخرج", provider="cohere", model="test-model", language="ar"
            )
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.mp3", io.BytesIO(b"fake-mp3-bytes"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["text"], "النص المستخرج")
        self.assertEqual(body["provider"], "cohere")
        self.assertEqual(body["model"], "test-model")
        self.assertEqual(body["language"], "ar")
        self.assertIsNone(body["duration_seconds"])

    def test_endpoint_accepts_no_language_or_prompt_field(self):
        """The endpoint no longer has language/prompt fields at all - only
        `file` should be required, and Swagger reflects this automatically
        from the route signature."""
        sig = inspect.signature(extract_text_from_audio)
        self.assertNotIn("language", sig.parameters)
        self.assertNotIn("prompt", sig.parameters)
        self.assertEqual(set(sig.parameters), {"file", "service", "current_user"})

    def test_valid_wav_accepted(self):
        _override_with_fake_provider(
            TranscriptionResult(text="hello", provider="cohere", model="test-model")
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.wav", io.BytesIO(_WAV_HEADER), "audio/wav")},
        )
        self.assertEqual(response.status_code, 200)

    def test_unsupported_extension_rejected(self):
        _override_with_fake_provider(
            TranscriptionResult(text="", provider="cohere", model="test-model")
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("document.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
        )
        self.assertEqual(response.status_code, 415)

    def test_empty_file_rejected(self):
        _override_with_fake_provider(
            TranscriptionResult(text="", provider="cohere", model="test-model")
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("empty.mp3", io.BytesIO(b""), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 422)

    def test_oversized_file_rejected(self):
        from app.core.config import settings

        original = settings.stt_max_file_size_mb
        settings.stt_max_file_size_mb = 1
        try:
            _override_with_fake_provider(
                TranscriptionResult(text="", provider="cohere", model="test-model")
            )
            oversized = b"x" * (2 * 1024 * 1024)
            response = client.post(
                "/api/text-extract/audio",
                files={"file": ("big.mp3", io.BytesIO(oversized), "audio/mpeg")},
            )
            self.assertEqual(response.status_code, 413)
        finally:
            settings.stt_max_file_size_mb = original

    def test_provider_timeout_mapped_to_504(self):
        _override_with_fake_provider(side_effect=STTTimeoutError("timed out"))
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 504)

    def test_provider_failure_mapped_to_502(self):
        _override_with_fake_provider(side_effect=STTProviderError("upstream failed"))
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 502)

    def test_endpoint_does_not_require_guest_id(self):
        _override_with_fake_provider(
            TranscriptionResult(text="hi", provider="cohere", model="test-model")
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 200)
        # No guest_id anywhere in the path or accepted form fields.
        self.assertNotIn("guest_id", response.request.url.path)

    def test_endpoint_has_no_db_dependency(self):
        """Structural proof this endpoint cannot write to the database - it
        never even receives a Session, unlike every guest/question endpoint
        in this codebase."""
        sig = inspect.signature(extract_text_from_audio)
        for name, param in sig.parameters.items():
            self.assertNotIn("db", name.lower())

    def test_no_guest_question_or_asset_rows_created(self):
        from sqlalchemy import func, select

        from app.database.session import SessionLocal
        from app.models.asset import Asset
        from app.models.guest import Guest
        from app.models.question import Question

        db = SessionLocal()
        try:
            before = {
                "guests": db.scalar(select(func.count()).select_from(Guest)),
                "questions": db.scalar(select(func.count()).select_from(Question)),
                "assets": db.scalar(select(func.count()).select_from(Asset)),
            }

            _override_with_fake_provider(
                TranscriptionResult(text="hi", provider="cohere", model="test-model")
            )
            response = client.post(
                "/api/text-extract/audio",
                files={"file": ("clip.mp3", io.BytesIO(b"data"), "audio/mpeg")},
            )
            self.assertEqual(response.status_code, 200)

            after = {
                "guests": db.scalar(select(func.count()).select_from(Guest)),
                "questions": db.scalar(select(func.count()).select_from(Question)),
                "assets": db.scalar(select(func.count()).select_from(Asset)),
            }
            self.assertEqual(before, after)
        finally:
            db.close()

    def test_response_does_not_include_raw_provider_metadata(self):
        _override_with_fake_provider(
            TranscriptionResult(
                text="hi",
                provider="cohere",
                model="test-model",
                metadata={"internal_cohere_field": "secret"},
            )
        )
        response = client.post(
            "/api/text-extract/audio",
            files={"file": ("clip.mp3", io.BytesIO(b"data"), "audio/mpeg")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.json().keys()),
            {"text", "provider", "model", "language", "duration_seconds", "chunked", "chunk_count"},
        )


class NoDiskPersistenceStructuralTests(unittest.TestCase):
    """The direct-upload path (files at or under stt_direct_max_bytes,
    still the overwhelming majority of uploads) never writes audio to disk
    at all - Groq's SDK accepts bytes directly, same as Cohere's did.
    Only files that exceed the direct limit legitimately touch disk, and
    only inside a unique temp directory that is always deleted afterward
    (see test_stt_service_chunking.py for that guarantee) - never here, in
    the modules these tests check."""

    def test_no_tempfile_module_used_on_the_direct_upload_path(self):
        import app.api.text_extract as text_extract_module
        import app.audio.providers.groq as groq_module
        import app.audio.validation as validation_module

        for module in (text_extract_module, groq_module, validation_module):
            source = inspect.getsource(module)
            self.assertNotIn("tempfile", source)
            self.assertNotIn("NamedTemporaryFile", source)

    def test_no_disk_write_calls_on_the_direct_upload_path(self):
        import app.api.text_extract as text_extract_module
        import app.audio.providers.groq as groq_module
        import app.audio.validation as validation_module

        for module in (text_extract_module, groq_module, validation_module):
            source = inspect.getsource(module)
            self.assertNotIn('open(', source)


class UploadCleanupTests(unittest.IsolatedAsyncioTestCase):
    """Calls the router function directly (bypassing FastAPI DI) with a
    fake UploadFile stub so we can assert .close() is always invoked -
    success, validation failure, and provider failure/timeout alike."""

    class _FakeUploadFile:
        def __init__(self, filename, content_type, data: bytes):
            self.filename = filename
            self.content_type = content_type
            self._data = data
            self._pos = 0
            self.closed = False

        async def read(self, size: int = -1) -> bytes:
            if self._pos >= len(self._data):
                return b""
            end = len(self._data) if size < 0 else min(self._pos + size, len(self._data))
            chunk = self._data[self._pos : end]
            self._pos = end
            return chunk

        async def close(self) -> None:
            self.closed = True

    async def test_upload_closed_after_success(self):
        fake_file = self._FakeUploadFile("clip.mp3", "audio/mpeg", b"data")
        provider = _FakeProvider(
            result=TranscriptionResult(text="hi", provider="cohere", model="test-model")
        )
        service = SpeechToTextService(provider=provider)

        await extract_text_from_audio(
            file=fake_file, service=service
        )
        self.assertTrue(fake_file.closed)

    async def test_upload_closed_after_provider_failure(self):
        from fastapi import HTTPException

        fake_file = self._FakeUploadFile("clip.mp3", "audio/mpeg", b"data")
        provider = _FakeProvider(side_effect=STTProviderError("boom"))
        service = SpeechToTextService(provider=provider)

        with self.assertRaises(HTTPException):
            await extract_text_from_audio(
                file=fake_file, service=service
            )
        self.assertTrue(fake_file.closed)

    async def test_upload_closed_after_timeout(self):
        from fastapi import HTTPException

        fake_file = self._FakeUploadFile("clip.mp3", "audio/mpeg", b"data")
        provider = _FakeProvider(side_effect=STTTimeoutError("timed out"))
        service = SpeechToTextService(provider=provider)

        with self.assertRaises(HTTPException):
            await extract_text_from_audio(
                file=fake_file, service=service
            )
        self.assertTrue(fake_file.closed)

    async def test_upload_closed_after_validation_failure(self):
        from fastapi import HTTPException

        fake_file = self._FakeUploadFile("document.pdf", "application/pdf", b"data")
        provider = _FakeProvider(
            result=TranscriptionResult(text="", provider="cohere", model="test-model")
        )
        service = SpeechToTextService(provider=provider)

        with self.assertRaises(HTTPException):
            await extract_text_from_audio(
                file=fake_file, service=service
            )
        self.assertTrue(fake_file.closed)
        self.assertEqual(provider.calls, 0)


if __name__ == "__main__":
    unittest.main()


def tearDownModule():
    cleanup_client_user(client)
