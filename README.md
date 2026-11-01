# AI Presentation Content Generator

Brief in -> validated slide content + speaker notes + PPTX out. Fully automated.

## Setup
```
pip install -r requirements.txt
cp .env.example .env      # put your GEMINI_API_KEY in .env
```
No key? It runs offline in mock mode (`PROVIDER=mock`).

## Run
| What | Command |
|---|---|
| Auto mode (folder watcher) | `python run.py watch`, then drop a `.txt`/`.md` brief into `inbox/` |
| Demo with sample brief | `python run.py demo` |
| One file | `python run.py file samples/club_update.txt` |
| Web UI | `streamlit run app/ui.py` |
| Tests (5 cases + 1 extra) | `pytest -v` |

## Flow
`inbox/` -> guard (clean, injection check) -> Gemini JSON -> Pydantic validation (repair retry x2) -> PPTX in `output/` -> run logged in SQLite (`data/slidegen.db`) -> brief moved to `processed/`.

## Files
- `app/prompts.py` structured + repair prompts
- `app/validator.py` input guard, output parsing
- `app/llm.py` Gemini + mock providers
- `app/storage.py` SQLite
- `app/pptx_builder.py` PPTX with notes + AI disclosure slide
- `app/pipeline.py` orchestration, `app/watcher.py` automation, `app/ui.py` demo UI
- `tests/test_cases.py` test suite
