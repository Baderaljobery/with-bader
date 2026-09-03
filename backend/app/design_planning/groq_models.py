from pydantic import BaseModel, ConfigDict

from app.core.json_schema import build_strict_json_schema

_CONFIG = ConfigDict(extra="forbid")


class GroqPlannedSlideSchema(BaseModel):
    model_config = _CONFIG

    headline: str
    body_text: str
    cta_text: str | None = None


class GroqSlidePlanSchema(BaseModel):
    """Deliberately does NOT ask Groq to echo back index/role - the caller
    (groq.py) zips the returned slides positionally against the exact
    requested slide_roles order instead, so a model mistake can never
    silently swap which slide is which."""

    model_config = _CONFIG

    slides: list[GroqPlannedSlideSchema]


GROQ_SLIDE_PLAN_JSON_SCHEMA = build_strict_json_schema(GroqSlidePlanSchema)
