"""LLM providers. Gemini for real use, Mock for offline tests/demo fallback."""
import json
import re
from typing import Protocol

from . import config


class Provider(Protocol):
    name: str

    def generate(self, system: str, user: str) -> str: ...


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        from google import genai
        from google.genai import types

        self._types = types
        self._client = genai.Client(api_key=api_key or config.GEMINI_API_KEY)
        self._model = model or config.GEMINI_MODEL

    def generate(self, system: str, user: str) -> str:
        resp = self._client.models.generate_content(
            model=self._model,
            contents=user,
            config=self._types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                temperature=0.4,
            ),
        )
        return resp.text or ""


class MockProvider:
    """Deterministic offline provider. Builds a plausible deck from the brief text."""

    name = "mock"

    def generate(self, system: str, user: str) -> str:
        m = re.search(r"<brief>\n(.*?)\n</brief>", user, re.S)
        brief = (m.group(1) if m else user).strip()
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", brief) if len(s.strip()) > 10]
        topic = (sentences[0] if sentences else brief)[:80].rstrip(".")
        chunks = [sentences[i : i + 2] for i in range(1, len(sentences), 2)] or [[topic]]
        slides = [
            {
                "title": topic[:90],
                "bullets": ["Overview of the brief", "Goals and context"],
                "speaker_notes": f"Welcome everyone. Today we cover: {topic}. I will walk through the key points from the brief in order.",
            }
        ]
        for i, ch in enumerate(chunks[:6], 1):
            bullets = [c[:150] for c in ch]
            if len(bullets) < 2:
                bullets.append("Key point from the brief")
            slides.append(
                {
                    "title": f"Key point {i}",
                    "bullets": bullets,
                    "speaker_notes": "Here we discuss: " + " ".join(ch)[:500] + " Let me explain why this matters to the audience.",
                }
            )
        slides.append(
            {
                "title": "Summary",
                "bullets": ["Recap of main points", "Next steps and questions"],
                "speaker_notes": "To summarise, we covered the main points from the brief. I am happy to take questions and discuss next steps now.",
            }
        )
        return json.dumps(
            {"deck_title": topic[:100], "audience": "General audience", "slides": slides, "unverified_claims": []}
        )


def get_provider(name: str | None = None) -> Provider:
    name = name or config.PROVIDER
    if name == "gemini":
        if not config.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY missing. Add it to .env or set PROVIDER=mock.")
        return GeminiProvider()
    return MockProvider()
