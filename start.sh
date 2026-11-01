#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=== AI Presentation Content Generator ==="
echo "Candidate: Kaushal Dinesh Rajmandai (Roll No: 150096725111)"
echo "Cohort: Sam Altman | Subject: AI and Prompt Engineering"
echo ""

if [ ! -d "venv" ]; then
    echo "[1/3] Setting up virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip -q
    ./venv/bin/pip install -r requirements.txt -q
else
    echo "[1/3] Environment already set up."
fi

echo "[2/3] Checking environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example (defaults to mock mode if no Gemini key)."
    fi
fi

echo "[3/3] Launching Streamlit web application..."
echo "Opening browser at http://localhost:8501"
./venv/bin/streamlit run app/ui.py
