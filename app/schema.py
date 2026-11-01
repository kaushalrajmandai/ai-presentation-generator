from typing import List

from pydantic import BaseModel, Field, field_validator


class Slide(BaseModel):
    title: str = Field(min_length=3, max_length=90)
    bullets: List[str] = Field(min_length=2, max_length=5)
    speaker_notes: str = Field(min_length=40, max_length=1200)

    @field_validator("bullets")
    @classmethod
    def bullets_not_blank(cls, v):
        cleaned = [b.strip() for b in v]
        if any(len(b) < 3 for b in cleaned):
            raise ValueError("bullets must be non-empty")
        if any(len(b) > 160 for b in cleaned):
            raise ValueError("bullet too long (max 160 chars)")
        return cleaned


class Deck(BaseModel):
    deck_title: str = Field(min_length=3, max_length=100)
    audience: str = Field(min_length=2, max_length=100)
    slides: List[Slide] = Field(min_length=3, max_length=15)
    unverified_claims: List[str] = Field(default_factory=list)
