/** Mirrors backend/app/audio/validation.py + app/core/config.py defaults
 * (STT_ALLOWED_EXTENSIONS / STT_MAX_FILE_SIZE_MB / STT_DIRECT_MAX_BYTES) -
 * not fetched dynamically, since the backend does not expose a config
 * endpoint for this. Frontend validation is UX only; the backend remains
 * the source of truth and re-validates independently.
 *
 * Shared by Text Extract and Guest Interview upload (Part 16 of the Groq
 * Whisper migration: one STT engine, one set of frontend limits - not
 * duplicated per feature).
 */
export const ALLOWED_AUDIO_EXTENSIONS = [
  ".flac",
  ".mp3",
  ".mp4",
  ".mpeg",
  ".mpga",
  ".m4a",
  ".ogg",
  ".wav",
  ".webm",
];

/** Files at or under this go straight to Groq Whisper in one request. */
export const DIRECT_UPLOAD_MAX_MB = 100;

/** Absolute cap - files over this are rejected outright. Anything between
 * the direct limit and this is automatically split into parts server-side
 * (see backend/app/audio/chunking.py) - the user never has to split
 * anything manually. */
export const MAX_FILE_SIZE_MB = 500;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const AUDIO_UPLOAD_HELP_TEXT = "ارفع ملفًا صوتيًا، وسنتولى معالجته واستخراج النص منه. يدعم النظام الملفات الصوتية بصيغ: " +
  ALLOWED_AUDIO_EXTENSIONS.join(", ")

export function formatFileSize(bytes: number): string {
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(mb < 1 ? 2 : 1)} ميجابايت`;
}

export function hasAllowedAudioExtension(filename: string): boolean {
  const lower = filename.toLowerCase();
  return ALLOWED_AUDIO_EXTENSIONS.some((ext) => lower.endsWith(ext));
}

export function validateAudioFile(file: File): string | null {
  if (!hasAllowedAudioExtension(file.name)) {
    return `صيغة غير مدعومة. الصيغ المدعومة: ${ALLOWED_AUDIO_EXTENSIONS.join(", ")}`;
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return `حجم الملف يتجاوز الحد الأقصى (${MAX_FILE_SIZE_MB} ميجابايت).`;
  }
  return null;
}
