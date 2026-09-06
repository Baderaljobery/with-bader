"""FFmpeg-based audio preprocessing and time-based chunking, used only for
uploads over settings.stt_direct_max_bytes (see app/audio/service.py). A
file at or under that limit never touches this module or the filesystem -
this is strictly the large-file path.

Every chunk is a real, independently-decodable audio file produced by
ffmpeg's segment muxer (never a raw byte slice of the original), and every
chunk is normalized to mono/16kHz FLAC first: mono + 16kHz alone
drastically shrinks typical stereo/44.1kHz source audio, and FLAC then
compresses that losslessly (unlike a lossy re-encode, this never degrades
speech quality) - both keep each chunk comfortably under the direct-upload
limit and speed up the upload to Groq.
"""

import asyncio
import shutil
from pathlib import Path

from app.audio.base import AudioProcessingError, FFmpegNotAvailableError

_CHUNK_FILENAME_PATTERN = "chunk_%04d.flac"


def ffmpeg_available() -> bool:
    """Runtime check, not an import-time assumption - see app/audio/
    service.py, which only calls this (and only raises
    FFmpegNotAvailableError) once a file actually needs chunking. A
    deployment that only ever receives files under the direct limit works
    fine without ffmpeg installed at all."""
    return shutil.which("ffmpeg") is not None


async def _run_ffmpeg(args: list[str]) -> None:
    process = await asyncio.create_subprocess_exec(
        "ffmpeg",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        detail = stderr.decode(errors="replace").strip().splitlines()
        last_lines = " | ".join(detail[-5:]) if detail else "no output"
        raise AudioProcessingError(f"ffmpeg failed (exit {process.returncode}): {last_lines}")


async def split_into_chunks(source_path: Path, output_dir: Path, chunk_minutes: int) -> list[Path]:
    """Normalizes source_path to mono/16kHz FLAC and splits it into
    sequential, non-overlapping chunk_minutes-long chunks in one ffmpeg
    pass, writing them into output_dir. Returns the chunk paths in
    chronological order (the segment muxer's own numbering is already
    chronological; sorting just makes that explicit and doesn't depend on
    glob ordering guarantees)."""
    if not ffmpeg_available():
        raise FFmpegNotAvailableError(
            "This audio file is larger than the direct-upload limit and needs to be split into "
            "parts before transcription, which requires ffmpeg - ffmpeg is not installed on this "
            "server. Files at or under the direct-upload limit do not require ffmpeg."
        )

    if chunk_minutes <= 0:
        raise AudioProcessingError("stt_chunk_minutes must be a positive number of minutes")

    output_pattern = output_dir / _CHUNK_FILENAME_PATTERN
    await _run_ffmpeg(
        [
            "-y",
            "-i",
            str(source_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "flac",
            "-f",
            "segment",
            "-segment_time",
            str(chunk_minutes * 60),
            "-reset_timestamps",
            "1",
            str(output_pattern),
        ]
    )

    chunks = sorted(output_dir.glob("chunk_*.flac"))
    if not chunks:
        raise AudioProcessingError(
            "ffmpeg did not produce any audio chunks - the uploaded file may be corrupted, "
            "empty of audio, or not a real audio file despite its extension"
        )
    return chunks
