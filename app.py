"""Streamlit Cloud entrypoint."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Directly execute app/ui.py in the main context
runpy.run_path(str(ROOT / "app" / "ui.py"), run_name="__main__")
