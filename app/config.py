import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

INBOX = ROOT / "inbox"
PROCESSED = ROOT / "processed"
OUTPUT = ROOT / "output"
DB_PATH = ROOT / "data" / "slidegen.db"

# Check standard environment variable or Streamlit secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
# "gemini" (default if a key exists) or "mock" (offline, deterministic)
PROVIDER = os.getenv("PROVIDER", "gemini" if GEMINI_API_KEY else "mock")

MIN_BRIEF_CHARS = 20
MAX_BRIEF_CHARS = 6000
MAX_RETRIES = 2

for d in (INBOX, PROCESSED, OUTPUT, DB_PATH.parent):
    d.mkdir(parents=True, exist_ok=True)
