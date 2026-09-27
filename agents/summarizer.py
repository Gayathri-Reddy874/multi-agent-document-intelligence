"""Abstractive summarization agent."""

import logging
from typing import Any, Dict, Optional

from transformers import pipeline

import config
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SummarizerAgent(BaseAgent):
    """Produces a short abstractive summary of the input text."""

    def __init__(self) -> None:
        super().__init__("Summary")
        self._model_name = config.SUMMARIZER_MODEL
        self._summarizer = None  # lazy-loaded

    def _get_summarizer(self):
        if self._summarizer is None:
            logger.info("Loading summarization model: %s", self._model_name)
            self._summarizer = pipeline("summarization", model=self._model_name)
        return self._summarizer

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"summary": "", "error": "empty input"}

        truncated = text[: config.SUMMARIZER_INPUT_CHAR_LIMIT]

        try:
            summarizer = self._get_summarizer()
            result = summarizer(
                truncated,
                max_length=config.SUMMARY_MAX_LENGTH,
                min_length=config.SUMMARY_MIN_LENGTH,
                do_sample=False,
            )
            return {"summary": result[0]["summary_text"]}
        except Exception as exc:
            logger.exception("Summarization failed")
            # Fall back to a naive truncation so downstream agents (e.g. the
            # fact checker, which consumes the summary) still get something.
            return {"summary": truncated[:200], "error": str(exc)}
