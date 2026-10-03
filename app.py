"""Streamlit front-end for the multi-agent document analysis system.

Visual design notes:
- The pipeline genuinely runs in sequence (summarize -> sentiment ->
  consistency check), so the numbered stage strip reflects a real order,
  not decoration.
- Each stage has its own accent color, reused consistently between the
  stage strip and its result panel, so the two visually connect.
- Custom HTML/CSS panels replace Streamlit's default st.info/success/warning
  boxes so verdicts read as part of one designed system rather than
  generic alert colors.
"""

import html
import logging

import streamlit as st

import config
from coordinator import Coordinator

logging.basicConfig(level=config.LOG_LEVEL)

st.set_page_config(page_title="Document Intelligence Pipeline", layout="wide")

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
BG = "#0F1319"
SURFACE = "#171C25"
SURFACE_RAISED = "#1D2430"
BORDER = "#2A3140"
TEXT = "#E8EBF1"
TEXT_MUTED = "#8A93A8"
ACCENT_SUMMARY = "#4FB6AC"    # stage 1 -- teal
ACCENT_SENTIMENT = "#E3A857"  # stage 2 -- amber
ACCENT_RISK = "#B15C6B"       # stage 3, risk-leaning verdict -- wine
ACCENT_NEUTRAL = "#7C8598"    # stage 3, neutral verdict -- slate

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background-color: {BG};
    color: {TEXT};
}}

section[data-testid="stSidebar"] {{ display: none; }}

.block-container {{
    max-width: 880px;
    padding-top: 2.5rem;
}}

/* Hero */
.dp-hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.3rem;
    color: {TEXT};
    margin-bottom: 0.3rem;
    letter-spacing: -0.01em;
}}
.dp-hero-sub {{
    color: {TEXT_MUTED};
    font-size: 1.02rem;
    max-width: 60ch;
    margin-bottom: 2rem;
}}

/* Pipeline strip */
.dp-pipeline {{
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 2.2rem;
}}
.dp-stage {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    flex: 1;
}}
.dp-stage-num {{
    width: 28px; height: 28px;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    font-weight: 500;
    flex-shrink: 0;
    color: {BG};
}}
.dp-stage-label {{
    font-size: 0.92rem;
    color: {TEXT_MUTED};
}}
.dp-stage-line {{
    height: 1px;
    background: {BORDER};
    flex: 0.4;
    margin: 0 0.4rem;
}}

/* Upload card */
div[data-testid="stFileUploader"] {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 1.1rem 1.2rem 0.6rem 1.2rem;
}}
div[data-testid="stFileUploader"] label {{
    color: {TEXT} !important;
    font-weight: 500;
}}

/* Buttons */
.stButton > button {{
    background: {ACCENT_SUMMARY};
    color: {BG};
    border: none;
    border-radius: 7px;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
}}
.stButton > button:hover {{
    background: #63C7BE;
    color: {BG};
}}

/* Text area (document preview) */
textarea {{
    background: {SURFACE} !important;
    color: {TEXT} !important;
    border-color: {BORDER} !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}}

/* Result panels */
.dp-panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-left: 3px solid var(--panel-accent);
    border-radius: 8px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.1rem;
}}
.dp-panel-head {{
    display: flex;
    align-items: baseline;
    gap: 0.55rem;
    margin-bottom: 0.7rem;
}}
.dp-panel-num {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--panel-accent);
}}
.dp-panel-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1.08rem;
    color: {TEXT};
}}
.dp-panel-note {{
    color: {TEXT_MUTED};
    font-size: 0.83rem;
    margin: -0.4rem 0 0.9rem 0;
}}
.dp-panel-body {{
    color: {TEXT};
    font-size: 0.96rem;
    line-height: 1.55;
}}
.dp-verdict {{
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    padding: 0.28rem 0.7rem;
    border-radius: 5px;
    background: var(--panel-accent);
    color: {BG};
    margin-bottom: 0.8rem;
}}
.dp-kv {{
    display: flex;
    gap: 2.2rem;
    margin-top: 0.3rem;
}}
.dp-kv-item .dp-kv-label {{
    color: {TEXT_MUTED};
    font-size: 0.78rem;
    margin-bottom: 0.15rem;
}}
.dp-kv-item .dp-kv-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.35rem;
    color: {TEXT};
}}
.dp-evidence {{
    background: {SURFACE_RAISED};
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    font-size: 0.88rem;
    color: {TEXT_MUTED};
    margin-top: 0.6rem;
    font-style: italic;
}}
.dp-error {{
    color: {ACCENT_RISK};
    font-size: 0.85rem;
    margin-bottom: 0.6rem;
}}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def stage_strip() -> None:
    stages = [
        (1, "Summarize", ACCENT_SUMMARY),
        (2, "Sentiment", ACCENT_SENTIMENT),
        (3, "Consistency check", ACCENT_NEUTRAL),
    ]
    parts = ["<div class='dp-pipeline'>"]
    for i, (num, label, color) in enumerate(stages):
        parts.append(
            f"<div class='dp-stage'>"
            f"<div class='dp-stage-num' style='background:{color}'>{num}</div>"
            f"<div class='dp-stage-label'>{label}</div>"
            f"</div>"
        )
        if i < len(stages) - 1:
            parts.append("<div class='dp-stage-line'></div>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def panel_open(num: str, title: str, accent: str, note: str = "") -> None:
    note_html = f"<div class='dp-panel-note'>{html.escape(note)}</div>" if note else ""
    st.markdown(
        f"<div class='dp-panel' style='--panel-accent:{accent}'>"
        f"<div class='dp-panel-head'>"
        f"<span class='dp-panel-num'>{num}</span>"
        f"<span class='dp-panel-title'>{title}</span>"
        f"</div>{note_html}<div class='dp-panel-body'>",
        unsafe_allow_html=True,
    )


def panel_close() -> None:
    st.markdown("</div></div>", unsafe_allow_html=True)


st.markdown("<div class='dp-hero-title'>Document Intelligence Pipeline</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='dp-hero-sub'>Upload a text document and three agents run in "
    "sequence — summarizing it, reading its tone, and scanning its language "
    "for risk signals.</div>",
    unsafe_allow_html=True,
)

stage_strip()


@st.cache_resource
def load_coordinator() -> Coordinator:
    return Coordinator()


coordinator = load_coordinator()

uploaded_file = st.file_uploader("Document (.txt)", type=["txt"])

if uploaded_file:
    try:
        text = uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        st.error("Couldn't read that file as UTF-8 text. Please upload a plain .txt file.")
        st.stop()

    if not text.strip():
        st.warning("The uploaded file is empty.")
        st.stop()

    with st.expander("Document preview", expanded=False):
        st.text_area("", text, height=220, label_visibility="collapsed")

    analyze = st.button("Run analysis")

    if analyze:
        with st.spinner("Running agents..."):
            try:
                results = coordinator.run_all(text)
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        # --- Stage 1: Summary ------------------------------------------
        summary = results["summary"]
        panel_open("01", "Summary", ACCENT_SUMMARY)
        if summary.get("error"):
            st.markdown(
                f"<div class='dp-error'>Summarizer had an issue: {html.escape(summary['error'])}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(html.escape(summary.get("summary", "(no summary produced)")))
        panel_close()

        # --- Stage 2: Sentiment ------------------------------------------
        sentiment = results["sentiment"]
        panel_open("02", "Sentiment", ACCENT_SENTIMENT)
        if sentiment.get("error"):
            st.markdown(
                f"<div class='dp-error'>Sentiment agent had an issue: {html.escape(sentiment['error'])}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<div class='dp-kv'>"
            f"<div class='dp-kv-item'><div class='dp-kv-label'>Label</div>"
            f"<div class='dp-kv-value'>{html.escape(sentiment.get('label', 'UNKNOWN'))}</div></div>"
            f"<div class='dp-kv-item'><div class='dp-kv-label'>Confidence</div>"
            f"<div class='dp-kv-value'>{sentiment.get('score', 0.0)}</div></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        panel_close()

        # --- Stage 3: Consistency check ------------------------------------
        fact = results["fact_check"]
        verdict_color = ACCENT_RISK if "Risk" in fact.get("verdict", "") else ACCENT_NEUTRAL
        if fact.get("verdict") == "Consistent Positive Report":
            verdict_color = ACCENT_SUMMARY
        panel_open(
            "03",
            "Consistency check",
            verdict_color,
            note="Keyword heuristic — not verification against an external source.",
        )
        if fact.get("error"):
            st.markdown(
                f"<div class='dp-error'>Consistency checker had an issue: {html.escape(fact['error'])}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<span class='dp-verdict'>{html.escape(fact['verdict'])}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(html.escape(fact["analysis"]))
            st.markdown(
                f"<div class='dp-evidence'>{html.escape(fact['evidence'])}</div>",
                unsafe_allow_html=True,
            )
        panel_close()


