"""CLI:  python run.py watch | python run.py file brief.txt | python run.py demo"""
import sys

from app import config
from app.pipeline import run_pipeline
from app.watcher import watch


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    if cmd == "watch":
        watch()
    elif cmd == "file":
        text = open(sys.argv[2], encoding="utf-8").read()
        r = run_pipeline(text, source=f"cli:{sys.argv[2]}")
        print("OK" if r.ok else "FAILED", r.pptx_path or r.error)
    elif cmd == "demo":
        import shutil
        for f in config.ROOT.joinpath("samples").glob("*.txt"):
            shutil.copy(f, config.INBOX / f.name)
        watch()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
