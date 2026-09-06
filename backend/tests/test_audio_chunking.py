import asyncio
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.audio.base import AudioProcessingError, FFmpegNotAvailableError
from app.audio.chunking import ffmpeg_available, split_into_chunks

_FFMPEG_AVAILABLE = ffmpeg_available()


def _make_sine_wave(path: Path, duration_seconds: int) -> None:
    """Generates a real, valid synthetic audio file via ffmpeg's built-in
    test-signal source (lavfi) - no binary fixture committed to the repo,
    and it's genuinely decodable audio, not a byte-slice trick."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=440:duration={duration_seconds}",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


@unittest.skipUnless(_FFMPEG_AVAILABLE, "ffmpeg is not installed on this machine")
class SplitIntoChunksTests(unittest.IsolatedAsyncioTestCase):
    async def test_short_file_under_chunk_duration_produces_one_chunk(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source = tmp_path / "source.wav"
            await asyncio.to_thread(_make_sine_wave, source, 3)

            chunks = await split_into_chunks(source, tmp_path, chunk_minutes=1)

            self.assertEqual(len(chunks), 1)
            self.assertTrue(chunks[0].is_file())
            self.assertGreater(chunks[0].stat().st_size, 0)

    async def test_long_file_splits_into_multiple_chronological_chunks(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source = tmp_path / "source.wav"
            await asyncio.to_thread(_make_sine_wave, source, 10)

            # chunk_minutes need not be a whole number - the service layer
            # always passes a real minute count, but the function itself
            # only ever multiplies by 60, so a fractional value here is a
            # legitimate way to exercise multi-chunk splitting without a
            # multi-minute fixture file.
            chunks = await split_into_chunks(source, tmp_path, chunk_minutes=4 / 60)

            self.assertEqual(len(chunks), 3)
            # Chronological order: the segment muxer already numbers them
            # sequentially, and split_into_chunks sorts on top of that.
            self.assertEqual([c.name for c in chunks], sorted(c.name for c in chunks))
            for chunk in chunks:
                self.assertGreater(chunk.stat().st_size, 0)

    async def test_produces_valid_independently_decodable_chunks(self):
        """Each chunk must be real audio ffmpeg can probe on its own - not
        a corrupted byte slice of the original."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source = tmp_path / "source.wav"
            await asyncio.to_thread(_make_sine_wave, source, 8)

            chunks = await split_into_chunks(source, tmp_path, chunk_minutes=3 / 60)

            for chunk in chunks:
                probe = subprocess.run(
                    ["ffmpeg", "-v", "error", "-i", str(chunk), "-f", "null", "-"],
                    capture_output=True,
                )
                self.assertEqual(probe.returncode, 0, probe.stderr.decode(errors="replace"))

    async def test_corrupted_input_raises_audio_processing_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source = tmp_path / "not-real-audio.wav"
            source.write_bytes(b"this is not a real audio file at all")

            with self.assertRaises(AudioProcessingError):
                await split_into_chunks(source, tmp_path, chunk_minutes=1)


class FFmpegAvailabilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_ffmpeg_raises_clear_configuration_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source = tmp_path / "source.wav"
            source.write_bytes(b"irrelevant - ffmpeg availability is checked first")

            with patch("app.audio.chunking.shutil.which", return_value=None):
                with self.assertRaises(FFmpegNotAvailableError):
                    await split_into_chunks(source, tmp_path, chunk_minutes=1)

    def test_ffmpeg_available_reflects_shutil_which(self):
        with patch("app.audio.chunking.shutil.which", return_value="/usr/bin/ffmpeg"):
            self.assertTrue(ffmpeg_available())
        with patch("app.audio.chunking.shutil.which", return_value=None):
            self.assertFalse(ffmpeg_available())


if __name__ == "__main__":
    unittest.main()
