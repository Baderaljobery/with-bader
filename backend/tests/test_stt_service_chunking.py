import subprocess
import unittest
from pathlib import Path

from app.audio.base import STTProviderError, SpeechToTextProvider
from app.audio.chunking import ffmpeg_available
from app.audio.models import AudioInput, TranscriptionResult
from app.audio.service import SpeechToTextService
from app.core.config import settings

_FFMPEG_AVAILABLE = ffmpeg_available()


def _audio(size_bytes: int) -> AudioInput:
    return AudioInput(filename="clip.wav", content_type="audio/wav", content=b"x" * size_bytes, size_bytes=size_bytes)


class _CountingFakeProvider(SpeechToTextProvider):
    """Returns a distinct, call-order-tagged text per invocation so a test
    can prove chunks were transcribed - and merged - in the right order,
    without ever hitting Groq."""

    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, texts: list[str] | None = None):
        self._texts = texts
        self.call_count = 0
        self.received_filenames: list[str] = []

    async def transcribe(self, audio, options=None):
        self.received_filenames.append(audio.filename)
        if self._texts is not None:
            text = self._texts[self.call_count]
        else:
            text = f"chunk-{self.call_count}"
        self.call_count += 1
        language = options.language if options and options.language else "ar"
        return TranscriptionResult(text=text, provider=self.provider_name, model=self.model_name, language=language)


class _FailingProvider(SpeechToTextProvider):
    provider_name = "fake"
    model_name = "fake-model"

    def __init__(self, fail_on_call: int):
        self._fail_on_call = fail_on_call
        self.call_count = 0

    async def transcribe(self, audio, options=None):
        self.call_count += 1
        if self.call_count == self._fail_on_call:
            raise STTProviderError("simulated upstream failure")
        return TranscriptionResult(text=f"chunk-{self.call_count}", provider=self.provider_name, model=self.model_name)


def _make_sine_wave(path: Path, duration_seconds: int) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_seconds}", str(path)],
        check=True,
        capture_output=True,
    )


class DirectPathTests(unittest.IsolatedAsyncioTestCase):
    """Files at or under stt_direct_max_bytes never touch ffmpeg/chunking -
    exactly the pre-existing (Cohere-era) behavior, unchanged."""

    async def test_file_under_direct_limit_calls_provider_once(self):
        provider = _CountingFakeProvider()
        service = SpeechToTextService(provider=provider)

        result = await service.transcribe(_audio(size_bytes=100))

        self.assertEqual(provider.call_count, 1)
        self.assertEqual(result.text, "chunk-0")
        self.assertIsNone(result.metadata)

    async def test_file_exactly_at_direct_limit_is_not_chunked(self):
        provider = _CountingFakeProvider()
        service = SpeechToTextService(provider=provider)

        await service.transcribe(_audio(size_bytes=settings.stt_direct_max_bytes))

        self.assertEqual(provider.call_count, 1)


@unittest.skipUnless(_FFMPEG_AVAILABLE, "ffmpeg is not installed on this machine")
class ChunkedPathTests(unittest.IsolatedAsyncioTestCase):
    """Forces the chunking path on a small real audio fixture by lowering
    stt_direct_max_bytes for the duration of each test, rather than needing
    an actual 100MB+ file - the chunking mechanics are identical regardless
    of why the file exceeded the threshold."""

    def setUp(self):
        self._original_direct_max = settings.stt_direct_max_bytes
        self._original_chunk_minutes = settings.stt_chunk_minutes

    def tearDown(self):
        settings.stt_direct_max_bytes = self._original_direct_max
        settings.stt_chunk_minutes = self._original_chunk_minutes

    async def _oversized_audio(self, tmp_path: Path, duration_seconds: int) -> AudioInput:
        source = tmp_path / "source.wav"
        _make_sine_wave(source, duration_seconds)
        content = source.read_bytes()
        settings.stt_direct_max_bytes = 10  # bytes - any real audio file exceeds this
        return AudioInput(filename="interview.wav", content_type="audio/wav", content=content, size_bytes=len(content))

    async def test_oversized_file_triggers_chunking_and_merges_in_order(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings.stt_chunk_minutes = 4 / 60
            audio = await self._oversized_audio(tmp_path, duration_seconds=10)

            provider = _CountingFakeProvider(texts=["الجزء الأول", "الجزء الثاني", "الجزء الثالث"])
            service = SpeechToTextService(provider=provider)

            result = await service.transcribe(audio)

            self.assertEqual(provider.call_count, 3)
            self.assertEqual(result.text, "الجزء الأول الجزء الثاني الجزء الثالث")
            self.assertEqual(result.metadata, {"chunked": True, "chunk_count": 3})
            # The merged result reports the language each chunk was
            # actually transcribed with, even though no explicit options
            # were passed by the caller (regression test - this used to
            # come back None because it was derived only from `options`).
            self.assertEqual(result.language, "ar")
            # Chunks handed to the provider in chronological filename order.
            self.assertEqual(provider.received_filenames, sorted(provider.received_filenames))

    async def test_empty_chunk_does_not_corrupt_merge(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings.stt_chunk_minutes = 4 / 60
            audio = await self._oversized_audio(tmp_path, duration_seconds=10)

            # Middle chunk transcribes as empty (e.g. silence) - must not
            # introduce a double space or stray leading/trailing space.
            provider = _CountingFakeProvider(texts=["الجزء الأول", "", "الجزء الثالث"])
            service = SpeechToTextService(provider=provider)

            result = await service.transcribe(audio)

            self.assertEqual(result.text, "الجزء الأول الجزء الثالث")

    async def test_one_chunk_failure_aborts_with_clean_error(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings.stt_chunk_minutes = 4 / 60
            audio = await self._oversized_audio(tmp_path, duration_seconds=10)

            provider = _FailingProvider(fail_on_call=2)
            service = SpeechToTextService(provider=provider)

            with self.assertRaises(STTProviderError):
                await service.transcribe(audio)

    async def test_temp_files_cleaned_up_after_success(self):
        import tempfile

        stt_tmp_dirs_before = {p.name for p in Path(tempfile.gettempdir()).glob("with-bader-stt-*")}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings.stt_chunk_minutes = 4 / 60
            audio = await self._oversized_audio(tmp_path, duration_seconds=6)

            provider = _CountingFakeProvider()
            service = SpeechToTextService(provider=provider)
            await service.transcribe(audio)

        stt_tmp_dirs_after = {p.name for p in Path(tempfile.gettempdir()).glob("with-bader-stt-*")}
        self.assertEqual(stt_tmp_dirs_before, stt_tmp_dirs_after)

    async def test_temp_files_cleaned_up_after_failure(self):
        import tempfile

        stt_tmp_dirs_before = {p.name for p in Path(tempfile.gettempdir()).glob("with-bader-stt-*")}

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings.stt_chunk_minutes = 4 / 60
            audio = await self._oversized_audio(tmp_path, duration_seconds=6)

            provider = _FailingProvider(fail_on_call=1)
            service = SpeechToTextService(provider=provider)
            with self.assertRaises(STTProviderError):
                await service.transcribe(audio)

        stt_tmp_dirs_after = {p.name for p in Path(tempfile.gettempdir()).glob("with-bader-stt-*")}
        self.assertEqual(stt_tmp_dirs_before, stt_tmp_dirs_after)


if __name__ == "__main__":
    unittest.main()
