from pathlib import Path

# Legacy local-filesystem storage location for AI-generated design images
# from the retired OpenRouter/Gemini image-generation path (see
# app/services/design_service.py's delete_design_draft) - the strict
# template-renderer flow that replaced it never writes here. Kept only so
# any pre-existing design_slides row with a real image_path can still be
# served (StaticFiles mount at MEDIA_URL_PREFIX, see app/main.py) and
# cleaned up on delete.
STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage" / "design-drafts"
MEDIA_URL_PREFIX = "/media/design-drafts"


def delete_generated_image(image_path: str | None) -> None:
    """Best-effort delete of a previously-saved image. Never raises if the
    file is already gone - deleting a design draft whose file was already
    removed (or was never on this filesystem) must not fail the request."""
    if not image_path or not image_path.startswith(f"{MEDIA_URL_PREFIX}/"):
        return
    filename = image_path.removeprefix(f"{MEDIA_URL_PREFIX}/")
    storage_root = STORAGE_DIR.resolve()
    file_path = (storage_root / filename).resolve()
    # Historical rows contain a relative media URL. Never let a malformed
    # or manually-edited row escape the configured storage directory.
    if not file_path.is_relative_to(storage_root) or file_path == storage_root:
        return
    file_path.unlink(missing_ok=True)
