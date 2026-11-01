"""End-to-end workflow:
brief -> clean/guard -> LLM -> validate (-> repair loop) -> PPTX -> store -> report."""
from dataclasses import dataclass, field
from pathlib import Path

from . import config, prompts, storage
from .llm import Provider, get_provider
from .pptx_builder import build_pptx
from .schema import Deck
from .validator import BriefRejected, clean_brief, parse_deck


@dataclass
class Result:
    ok: bool
    run_id: int
    deck: Deck | None = None
    pptx_path: Path | None = None
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    attempts: int = 0


def run_pipeline(brief: str, *, source="manual", audience="General audience", n_slides=6,
                 provider: Provider | None = None, out_dir: Path | None = None,
                 db_path=None) -> Result:
    provider = provider or get_provider()
    out_dir = out_dir or config.OUTPUT
    n_slides = max(3, min(int(n_slides), 12))

    try:
        cleaned, warnings = clean_brief(brief)
    except BriefRejected as e:
        rid = storage.save_run(source=source, brief=brief or "", provider=provider.name,
                               status="rejected", error=str(e), db_path=db_path)
        return Result(False, rid, error=str(e))

    system = prompts.SYSTEM_PROMPT.format(min_slides=3, max_slides=n_slides + 2)
    user = prompts.USER_PROMPT.format(audience=audience, n_slides=n_slides, brief=cleaned)

    raw, deck, last_err, attempts = "", None, None, 0
    for attempts in range(1, config.MAX_RETRIES + 2):
        try:
            raw = provider.generate(system, user)
            deck = parse_deck(raw)
            break
        except ValueError as e:  # validation failure -> refine prompt and retry
            last_err = str(e)
            user = prompts.REPAIR_PROMPT.format(errors=last_err, previous=raw[:3000])
        except Exception as e:  # network/API failure
            last_err = f"LLM call failed: {e}"
            break

    if deck is None:
        rid = storage.save_run(source=source, brief=cleaned, provider=provider.name, status="failed",
                               attempts=attempts, warnings=warnings, error=last_err, db_path=db_path)
        return Result(False, rid, warnings=warnings, error=last_err, attempts=attempts)

    import time
    stem = f"{int(time.time())}-{deck.deck_title[:30]}".replace(" ", "-").lower()
    path = build_pptx(deck, out_dir, stem=stem)
    rid = storage.save_run(source=source, brief=cleaned, provider=provider.name, status="success",
                           attempts=attempts, deck=deck, pptx_path=path, warnings=warnings, db_path=db_path)
    return Result(True, rid, deck=deck, pptx_path=path, warnings=warnings, attempts=attempts)
