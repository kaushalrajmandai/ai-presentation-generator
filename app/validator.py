"""Input guards (responsible AI) and output validation."""
import json
import re

from pydantic import ValidationError

from . import config
from .schema import Deck

INJECTION_PATTERNS = [
    r"ignore (all |any )?(previous|prior|above) (instructions|prompts?)",
    r"disregard (the )?(system|previous) (prompt|instructions)",
    r"reveal (your )?(system )?prompt",
    r"you are now (?:a|an|in) ",
    r"developer mode",
    r"act as (?:a|an) (?!presentation)",
]


class BriefRejected(Exception):
    """Brief is unusable (empty/too short). Never sent to the model."""


def clean_brief(text: str) -> tuple[str, list[str]]:
    """Return (sanitized_brief, warnings). Raises BriefRejected for unusable input."""
    warnings: list[str] = []
    text = (text or "").replace("\x00", "").strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) < config.MIN_BRIEF_CHARS:
        raise BriefRejected(
            f"Brief too short ({len(text)} chars). Provide at least {config.MIN_BRIEF_CHARS}."
        )
    if len(re.findall(r"[A-Za-zऀ-ॿ]{3,}", text)) < 3:
        raise BriefRejected("Brief has no readable content.")

    if len(text) > config.MAX_BRIEF_CHARS:
        text = text[: config.MAX_BRIEF_CHARS]
        warnings.append(f"Brief truncated to {config.MAX_BRIEF_CHARS} characters.")

    for pat in INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            warnings.append("Possible prompt-injection text detected and neutralised.")
            text = re.sub(pat, "[removed-instruction]", text, flags=re.IGNORECASE)
    # stop the brief from closing our data delimiter
    text = text.replace("</brief>", "").replace("<brief>", "")
    return text, warnings


def parse_deck(raw: str) -> Deck:
    """Parse model output into a validated Deck. Raises ValueError with readable errors."""
    raw = (raw or "").strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Output is not valid JSON: {e}")
    try:
        return Deck.model_validate(data)
    except ValidationError as e:
        msgs = [f"{'.'.join(map(str, err['loc']))}: {err['msg']}" for err in e.errors()]
        raise ValueError("; ".join(msgs))
