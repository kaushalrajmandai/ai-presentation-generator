@echo off
echo =======================================================
echo AI Presentation Content Generator
echo Candidate: Kaushal Dinesh Rajmandai (Roll No: 150096725111)
echo Cohort: Sam Altman ^| Subject: AI and Prompt Engineering
echo =======================================================
echo.

IF NOT EXIST "venv" (
    echo [1/3] Setting up Python virtual environment...
    python -m venv venv
    call venv\Scripts\pip install --upgrade pip
    call venv\Scripts\pip install -r requirements.txt
) ELSE (
    echo [1/3] Python environment already configured.
)

echo.
echo [2/3] Checking environment configuration...
IF NOT EXIST ".env" (
    IF EXIST ".env.example" (
        copy .env.example .env
        echo Created .env from .env.example
    )
)

echo.
echo [3/3] Starting Streamlit Application...
call venv\Scripts\streamlit run app/ui.py
pause
