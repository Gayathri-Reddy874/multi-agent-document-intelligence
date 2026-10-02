"""Sentiment classification agent."""

import logging
from typing import Any, Dict, Optional

from transformers import pipeline

import config
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SentimentAgent(BaseAgent):
    """Classifies text sentiment using a pretrained RoBERTa model.

    Note: cardiffnlp/twitter-roberta-base-sentiment-latest already returns
    human-readable labels ("negative", "neutral", "positive") rather than
    "LABEL_0/1/2" style outputs, so no relabeling is needed. The original
    version of this agent mapped LABEL_0/1/2 -> NEGATIVE/NEUTRAL/POSITIVE,
    which never matched the model's real output and silently fell back to
    returning the raw label unchanged.
    """

    def __init__(self) -> None:
        super().__init__("Sentiment")
        self._model_name = config.SENTIMENT_MODEL
        self._analyzer = None  # lazy-loaded so importing this module is cheap

    def _get_analyzer(self):
        if self._analyzer is None:
            logger.info("Loading sentiment model: %s", self._model_name)
            self._analyzer = pipeline("text-classification", model=self._model_name)
        return self._analyzer

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"label": "NEUTRAL", "score": 0.0, "error": "empty input"}

        try:
            analyzer = self._get_analyzer()
            result = analyzer(text[: config.SENTIMENT_INPUT_CHAR_LIMIT])[0]
            return {
                "label": result["label"].upper(),
                "score": round(float(result["score"]), 4),
            }
        except Exception as exc:  # model errors shouldn't crash the whole pipeline
            logger.exception("Sentiment analysis failed")
            return {"label": "UNKNOWN", "score": 0.0, "error": str(exc)}


