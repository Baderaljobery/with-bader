from typing import Literal

from pydantic import BaseModel, Field

ContentPlatform = Literal["linkedin", "x", "instagram", "general"]
ContentLength = Literal["short", "medium", "detailed"]
ContentContextCategory = Literal["answers", "notebook", "transcript", "research", "questions"]


class ContentContextItem(BaseModel):
    """One compact, ID-tagged piece of grounding context drawn from a
    guest's already-existing data (never freshly researched/browsed here).
    `category` is what powers the frontend's "sources used" transparency."""

    id: str
    category: ContentContextCategory
    text: str


class ContentGenerationOptions(BaseModel):
    platform: ContentPlatform
    length: ContentLength
    language: str
    custom_instructions: str | None = None


class ContentGenerationResult(BaseModel):
    title: str | None = None
    content: str
