import asyncio
import logging
import tempfile
import uuid
from pathlib import Path

from app.audio.base import SpeechToTextProvider
from app.audio.chunking import split_into_chunks
from app.audio.models import AudioInput, TranscriptionOptions, TranscriptionResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Provider-independent entry point for all STT consumers - the
    General Text Extract tool (app/api/text_extract.py) and the Guest
    Interview workspace (app/api/guest_interview.py) both call this exact
    same service, never a concrete provider directly.

    Also the single place large-file chunking lives: a caller always hands
    over one AudioInput and gets back one TranscriptionResult, whether that
    took one request to the provider or several sequential ones under the
    hood. Neither API endpoint needs to know or care which happened.
    """

    def __init__(self, provider: SpeechToTextProvider) -> None:
        self.provider = provider

    async def transcribe(
        self, audio: AudioInput, options: TranscriptionOptions | None = None
    ) -> TranscriptionResult:
        if audio.size_bytes <= settings.stt_direct_max_bytes:
            return await self.provider.transcribe(audio, options)
        return await self._transcribe_chunked(audio, options)

    async def _transcribe_chunked(
        self, audio: AudioInput, options: TranscriptionOptions | None
    ) -> TranscriptionResult:
        """Files over settings.stt_direct_max_bytes: write to a unique temp
        directory (never a shared/predictable path), normalize + split via
        ffmpeg, transcribe each chunk sequentially in chronological order,
        merge the resulting text deterministically, then delete the entire
        temp directory - on success or failure alike, via the context
        manager. No audio (source or chunks) ever outlives this call."""
        with tempfile.TemporaryDirectory(prefix="with-bader-stt-") as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_path = tmp_path / f"source-{uuid.uuid4().hex}"
            await asyncio.to_thread(source_path.write_bytes, audio.content)

            chunk_paths = await split_into_chunks(source_path, tmp_path, settings.stt_chunk_minutes)

            logger.info(
                "stt chunking started provider=%s filename=%s size_bytes=%d chunk_count=%d",
                self.provider.provider_name,
                audio.filename,
                audio.size_bytes,
                len(chunk_paths),
            )

            texts: list[str] = []
            language: str | None = None
            for index, chunk_path in enumerate(chunk_paths, start=1):
                chunk_bytes = await asyncio.to_thread(chunk_path.read_bytes)
                chunk_audio = AudioInput(
                    filename=chunk_path.name,
                    content_type="audio/flac",
                    content=chunk_bytes,
                    size_bytes=len(chunk_bytes),
                )
                logger.info(
                    "stt chunk transcribe index=%d/%d filename=%s",
                    index,
                    len(chunk_paths),
                    audio.filename,
                )
                # Sequential by design (Part 6 of the spec this implements):
                # a single provider rate limit or transient failure aborts
                # the whole request with one clear error rather than
                # juggling partial results from concurrent chunk requests.
                chunk_result = await self.provider.transcribe(chunk_audio, options)
                texts.append(chunk_result.text.strip())
                if language is None:
                    # Every chunk was transcribed with the same explicit
                    # language (the same `options` passed through to each
                    # one) - read it back from the provider's own result
                    # rather than only from `options`, so it's correct even
                    # when the caller didn't pass options at all and the
                    # provider fell back to its own configured default.
                    language = chunk_result.language

        # Deterministic merge: drop empty chunks (silence/no speech), join
        # the rest with a single space. No LLM rewriting, no fuzzy
        # de-duplication - see the spec's Part 10/11 for why this stays
        # simple for v1.
        merged_text = " ".join(text for text in texts if text)

        return TranscriptionResult(
            text=merged_text,
            language=language,
            duration_seconds=None,
            provider=self.provider.provider_name,
            model=self.provider.model_name,
            segments=None,
            metadata={"chunked": True, "chunk_count": len(chunk_paths)},
        )


def get_speech_to_text_service() -> SpeechToTextService:
    """Single wiring point for the provider implementation. Swap via
    STT_PROVIDER - SpeechToTextService itself never changes."""
    from app.audio.factory import build_stt_provider

    return SpeechToTextService(provider=build_stt_provider())
