"""Automated action: drop a brief (.txt/.md) into inbox/ and the pipeline runs by itself.
Result: PPTX in output/, row in SQLite, brief moved to processed/."""
import shutil
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from . import config
from .pipeline import run_pipeline

EXTS = {".txt", ".md"}


def process_file(path):
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    res = run_pipeline(text, source=f"inbox:{path.name}")
    config.PROCESSED.mkdir(exist_ok=True)
    shutil.move(str(path), config.PROCESSED / f"{res.run_id}_{path.name}")
    status = f"OK -> {res.pptx_path.name}" if res.ok else f"FAILED: {res.error}"
    print(f"[watcher] {path.name}: {status}", flush=True)
    return res


class _Handler(FileSystemEventHandler):
    def on_created(self, event):
        p = Path(event.src_path)
        if not event.is_directory and p.suffix.lower() in EXTS:
            time.sleep(0.5)  # let the writer finish
            process_file(p)


def watch():
    # process anything already waiting
    for f in sorted(config.INBOX.iterdir()):
        if f.suffix.lower() in EXTS:
            process_file(f)
    obs = Observer()
    obs.schedule(_Handler(), str(config.INBOX), recursive=False)
    obs.start()
    print(f"[watcher] watching {config.INBOX} (provider={config.PROVIDER}). Ctrl+C to stop.", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


if __name__ == "__main__":
    watch()
