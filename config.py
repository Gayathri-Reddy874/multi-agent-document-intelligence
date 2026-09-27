"""
Central configuration for the multi-agent system.

Keeping model names, thresholds, and limits in one place means they can be
overridden via environment variables (e.g. in Docker or CI) without touching
agent code.
"""

import os

# --- Model configuration -----------------------------------------------
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
SENTIMENT_MODEL = os.getenv(
    "SENTIMENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# --- Summarizer limits ---------------------------------------------------
SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", 100))
SUMMARY_MIN_LENGTH = int(os.getenv("SUMMARY_MIN_LENGTH", 30))
SUMMARIZER_INPUT_CHAR_LIMIT = 1024  # bart-large-cnn's practical input window

# --- Sentiment limits ------------------------------------------------------
SENTIMENT_INPUT_CHAR_LIMIT = 512

# --- Fact / consistency checker keyword lists -----------------------------
# NOTE: this agent is a lightweight heuristic keyword scorer, not a true
# fact-checker (it does not verify claims against any external source).
# It flags language that suggests a positive vs. risk-indicating report.
POSITIVE_KEYWORDS = ["excellent", "good", "great", "no issues", "operational"]
NEGATIVE_KEYWORDS = ["average", "however", "problem", "latency", "noisy", "issue", "fail"]

# --- Logging ---------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
