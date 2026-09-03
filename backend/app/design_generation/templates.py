from pathlib import Path

# Mirrors frontend/features/design/lib/template-registry.ts's `references`
# field exactly. Kept as a small duplicated mapping (same convention as
# other frontend/backend enum duplication in this codebase, e.g. the
# DesignPlatform Literal) rather than importing frontend TypeScript from
# the backend. Update both together whenever templates.ts changes.
TEMPLATE_REFERENCE_FILES: dict[str, list[str]] = {
    "template-01": ["template-01/reference-01.png"],
    "template-02": ["template-02/reference-01.jpg"],
    "template-03": ["template-03/reference-01.png"],
    "template-04": ["template-04/reference-01.jpg"],
}

TEMPLATE_IDS: tuple[str, ...] = tuple(TEMPLATE_REFERENCE_FILES.keys())

# Computed relative to this file (never a hardcoded absolute/Windows path)
# so it resolves correctly on any developer machine or deployment target -
# backend/app/design_generation/templates.py -> parents[3] is the repo root.
_DESIGN_REFERENCES_ROOT = (
    Path(__file__).resolve().parents[3] / "frontend" / "public" / "design-references"
)

_MIME_TYPES_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


class TemplateReferenceNotFoundError(Exception):
    """Raised when template_id is unknown, or its reference image file(s)
    are missing from disk."""


def load_template_reference_images(template_id: str) -> list[tuple[bytes, str]]:
    """Returns [(image_bytes, mime_type), ...] for the given template,
    reading the actual reference image bytes server-side from the shared
    frontend/public asset directory. Never passes a filename/description to
    the model and pretends it "saw" the image - the real bytes are
    supplied as multimodal input (see openrouter.py)."""
    relative_paths = TEMPLATE_REFERENCE_FILES.get(template_id)
    if not relative_paths:
        raise TemplateReferenceNotFoundError(f"Unknown design template '{template_id}'")

    root = _DESIGN_REFERENCES_ROOT.resolve()
    results: list[tuple[bytes, str]] = []
    for relative_path in relative_paths:
        file_path = (root / relative_path).resolve()
        if root not in file_path.parents:
            raise TemplateReferenceNotFoundError(
                f"Invalid reference path for template '{template_id}'"
            )
        if not file_path.is_file():
            raise TemplateReferenceNotFoundError(
                f"Reference image not found on disk for template '{template_id}': {relative_path}"
            )
        mime_type = _MIME_TYPES_BY_SUFFIX.get(file_path.suffix.lower(), "image/png")
        results.append((file_path.read_bytes(), mime_type))
    return results
