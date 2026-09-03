from pydantic import BaseModel, ConfigDict

from app.core.json_schema import build_strict_json_schema

_CONFIG = ConfigDict(extra="forbid")


class GroqContentGenerationSchema(BaseModel):
    """The exact shape requested from Groq via JSON-schema structured
    output. `title` is nullable (many platforms - X, Instagram - genuinely
    have no title) but still "required" to appear in strict-schema terms;
    see app/core/json_schema.py's docstring for why that's not the same as
    "must be non-null"."""

    model_config = _CONFIG

    title: str | None = None
    content: str


GROQ_CONTENT_GENERATION_JSON_SCHEMA = build_strict_json_schema(GroqContentGenerationSchema)
