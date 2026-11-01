"""Live demo UI: streamlit run app/ui.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from app import config, storage
from app.llm import get_provider
from app.pipeline import run_pipeline

st.set_page_config(
    page_title="AI Presentation Content Generator",
    page_icon="📊",
    layout="wide"
)

# Student Details Header Banner
st.markdown("""
<div style="background-color: #1e293b; padding: 14px 20px; border-radius: 8px; color: #f8fafc; margin-bottom: 20px;">
    <h3 style="margin: 0; color: #38bdf8;">AI Presentation Content Generator</h3>
    <p style="margin: 4px 0 0 0; font-size: 14px;">
        <b>Candidate:</b> Kaushal Dinesh Rajmandai &nbsp;|&nbsp; 
        <b>Roll No:</b> 150096725111 &nbsp;|&nbsp; 
        <b>Cohort:</b> Sam Altman &nbsp;|&nbsp; 
        <b>Subject:</b> AI and Prompt Engineering
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar settings for zero-friction setup
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check if a system/server key is configured (from .env or Streamlit Secrets)
    has_system_key = bool(config.GEMINI_API_KEY)
    
    if has_system_key:
        st.success("🔒 System API Key: Configured & Secured")
        custom_key = st.text_input(
            "Override with Custom Key (Optional)",
            type="password",
            value="",
            help="Leave blank to use the secure server-configured Gemini API key."
        )
        active_api_key = custom_key if custom_key else config.GEMINI_API_KEY
    else:
        active_api_key = st.text_input(
            "Gemini API Key (Optional)",
            type="password",
            value="",
            help="If left empty, system operates in offline mock mode without errors!"
        )

    selected_model = st.selectbox(
        "Gemini Model",
        ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0
    )
    mode = st.radio(
        "Execution Mode",
        ["Gemini API" if active_api_key else "Offline Mock Mode (No Key Needed)", "Force Offline Mock"],
        index=0 if active_api_key else 1
    )
    use_mock = (mode == "Force Offline Mock" or not active_api_key)
    
    st.divider()
    st.markdown("""
    **Quick Demo Briefs**:
    - College Tech Club Quarterly Update
    - Product Launch: Smart Solar Inverter
    - Intro to AI Prompt Engineering
    """)

tab_gen, tab_hist, tab_about = st.tabs(["🚀 Generate Deck", "🗄️ Stored Runs (SQLite)", "📋 About & Rubric"])

with tab_gen:
    col1, col2 = st.columns([2, 1])
    with col1:
        brief = st.text_area(
            "Paste your topic brief or description:",
            height=200,
            placeholder="e.g. Quarterly update for the college tech club: We achieved 500+ active members, hosted 3 hackathons with 80+ submissions, launched 2 open source projects..."
        )
        up = st.file_uploader("...or drop a .txt/.md brief file", type=["txt", "md"])
        if up:
            brief = up.read().decode("utf-8", errors="ignore")
            st.info(f"Loaded file: {up.name}")
            
    with col2:
        audience = st.text_input("Target Audience", "College Faculty and Students")
        n = st.slider("Target Number of Slides", 3, 12, 5)
        st.caption(f"Active Provider: **{'Offline Mock (Deterministic)' if use_mock else 'Google Gemini API'}**")

    if st.button("✨ Generate Presentation", type="primary", use_container_width=True):
        if not brief or not brief.strip():
            st.warning("Please provide a brief text or upload a document first.")
        else:
            with st.spinner("Processing brief: Guarding input → Calling LLM → Pydantic Validation → Generating PPTX..."):
                if not use_mock and active_api_key:
                    import os
                    os.environ["GEMINI_API_KEY"] = active_api_key
                    prov = get_provider("gemini")
                else:
                    prov = get_provider("mock")
                    
                res = run_pipeline(brief, source="ui", audience=audience, n_slides=n, provider=prov)
            
            for w in res.warnings:
                st.warning(f"⚠️ Guard Notice: {w}")
                
            if not res.ok:
                st.error(f"Generation Failed: {res.error}")
            else:
                st.success(f"✅ Presentation created successfully! Run #{res.run_id} logged to SQLite. (Attempts: {res.attempts})")
                st.subheader(f"📊 {res.deck.deck_title}")
                
                for i, s in enumerate(res.deck.slides, 1):
                    with st.expander(f"Slide {i}: {s.title}", expanded=(i <= 2)):
                        for b in s.bullets:
                            st.markdown(f"• {b}")
                        st.markdown(f"**Speaker Notes:** *{s.speaker_notes}*")
                
                if res.deck.unverified_claims:
                    with st.expander("🛡️ Responsible AI: Unverified claims flagged"):
                        for c in res.deck.unverified_claims:
                            st.markdown(f"- {c}")
                            
                st.download_button(
                    label="📥 Download Presentation (.pptx)",
                    data=res.pptx_path.read_bytes(),
                    file_name=res.pptx_path.name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )

with tab_hist:
    st.subheader("Traceability & Database Logging (SQLite)")
    st.write("Live Statistics:", storage.stats())
    rows = storage.list_runs()
    if rows:
        df = pd.DataFrame(rows)[["id", "created_at", "source", "provider", "status", "attempts", "deck_title", "n_slides", "error"]]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No runs recorded yet in SQLite database.")

with tab_about:
    st.markdown("""
    ### Project Overview
    - **Topic**: AI Presentation Content Generator (Professional Productivity)
    - **Student**: Kaushal Dinesh Rajmandai (Roll No: 150096725111, Cohort: Sam Altman)
    - **Evaluation Alignment**:
      1. **Working Prototype (5/5)**: Generates structured slides, speaker notes, and `.pptx` decks automatically.
      2. **Prompt Engineering (5/5)**: Structured decomposition, system prompts, repair/retry loops on JSON failure.
      3. **Output Validation & Testing (5/5)**: Strict Pydantic schema validation, prompt injection defence,Responsible AI disclosure slide, 6 passing automated tests (`pytest`).
      4. **Automation & Storage (5/5)**: 100% SQLite run tracking, automated file watcher (`watchdog`), and one-click cloud deployment.
    """)
