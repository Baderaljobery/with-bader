from typing import Protocol

from app.audio.base import STTFileTooLargeError, STTUnsupportedFormatError, STTValidationError
from app.core.config import settings


# Matches Groq's officially supported speech-to-text formats exactly
# (console.groq.com/docs/speech-to-text, verified 2026-09-06):
# flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm.
_DEFAULT_ALLOWED_EXTENSIONS = (
    ".flac",
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".ogg",
    ".wav",
    ".webm",
)

_ALLOWED_CONTENT_TYPES = (
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/flac",
    "audio/x-flac",
    "audio/ogg",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a",
    "audio/webm",
    "video/mp4",
    "video/webm",
)

# Generic/placeholder content-types many clients send when they don't know
# (or don't bother setting) the real one - not disqualifying on their own,
# since the extension is the authoritative check.
_GENERIC_CONTENT_TYPES = {"application/octet-stream", "binary/octet-stream", ""}


class _AsyncReadable(Protocol):
    async def read(self, size: int = -1) -> bytes: ...


def allowed_extensions() -> tuple[str, ...]:
    raw = settings.stt_allowed_extensions
    if not raw:
        return _DEFAULT_ALLOWED_EXTENSIONS
    return tuple(ext.strip().lower() for ext in raw.split(",") if ext.strip())


def validate_filename_and_content_type(filename: str | None, content_type: str | None) -> None:
    """MIME type alone is not trusted - clients often send generic or
    missing content types - so the file extension is the authoritative
    check. A content-type that IS present and specific but doesn't match
    any allowed audio type is still rejected."""
    if not filename or "." not in filename:
        raise STTUnsupportedFormatError("Audio file must have a recognizable file extension")

    extension = "." + filename.rsplit(".", 1)[-1].lower()
    allowed = allowed_extensions()
    if extension not in allowed:
        raise STTUnsupportedFormatError(
            f"Unsupported audio file extension '{extension}' (allowed: {', '.join(allowed)})"
        )

    normalized_content_type = (content_type or "").split(";")[0].strip().lower()
    if normalized_content_type and normalized_content_type not in _GENERIC_CONTENT_TYPES:
        if normalized_content_type not in _ALLOWED_CONTENT_TYPES:
            raise STTUnsupportedFormatError(
                f"Unsupported content type '{content_type}' for audio upload"
            )


def validate_file_size(size_bytes: int) -> None:
    if size_bytes <= 0:
        raise STTValidationError("Uploaded audio file is empty")

    max_bytes = settings.stt_max_file_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise STTFileTooLargeError(
            f"Audio file is {size_bytes} bytes, which exceeds the "
            f"{settings.stt_max_file_size_mb}MB limit"
        )


async def read_bounded_upload(
    upload: _AsyncReadable, max_bytes: int, chunk_size: int = 1024 * 1024
) -> bytes:
    """Reads an upload into memory, aborting as soon as it exceeds max_bytes
    rather than buffering an arbitrarily large file just to reject it.
    Nothing is ever written to disk by this function."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await upload.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise STTFileTooLargeError(
                f"Audio file exceeds the configured size limit of {max_bytes} bytes"
            )
        chunks.append(chunk)
    return b"".join(chunks)
