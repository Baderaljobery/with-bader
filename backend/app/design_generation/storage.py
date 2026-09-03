import uuid
from pathlib import Path

# Simple local-filesystem storage for generated design images - no S3, no
# CDN, this is a first version. Files live under backend/storage/design-
# drafts/ and are served back out by a StaticFiles mount at MEDIA_URL_PREFIX
# (see app/main.py). Swapping this for object storage later only means
# rewriting this one module - callers only ever see the returned URL path.
STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "design-drafts"
MEDIA_URL_PREFIX = "/media/design-drafts"

_EXTENSION_BY_MIME_TYPE = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
}


def save_generated_image(image_bytes: bytes, mime_type: str) -> str:
    """Writes the generated image to disk and returns its server-relative
    URL path (e.g. "/media/design-drafts/<uuid>.png")."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    extension = _EXTENSION_BY_MIME_TYPE.get(mime_type, ".png")
    filename = f"{uuid.uuid4()}{extension}"
    (STORAGE_DIR / filename).write_bytes(image_bytes)
    return f"{MEDIA_URL_PREFIX}/{filename}"


def delete_generated_image(image_path: str | None) -> None:
    """Best-effort delete of a previously-saved image. Never raises if the
    file is already gone - deleting a design draft whose file was already
    removed (or was never on this filesystem) must not fail the request."""
    if not image_path or not image_path.startswith(f"{MEDIA_URL_PREFIX}/"):
        return
    filename = image_path.removeprefix(f"{MEDIA_URL_PREFIX}/")
    file_path = STORAGE_DIR / filename
    file_path.unlink(missing_ok=True)
