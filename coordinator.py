"""Orchestrates the agent pipeline: summarize -> sentiment -> consistency check."""

import logging
from typing import Any, Dict

from agents.summarizer import SummarizerAgent
from agents.sentiment import SentimentAgent
from agents.fact_checker import FactCheckerAgent

logger = logging.getLogger(__name__)


class Coordinator:
    """Runs each agent over a document and assembles their results.

    Each agent call is wrapped so that a failure in one agent (e.g. a model
    download error) doesn't take down the whole pipeline — the caller gets a
    partial result with an "error" key on the failed agent instead of an
    unhandled exception.
    """

    def __init__(self) -> None:
        self.summarizer = SummarizerAgent()
        self.sentiment = SentimentAgent()
        self.fact_checker = FactCheckerAgent()

    def run_all(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            raise ValueError("Cannot analyze empty document text.")

        summary = self._safe_run(self.summarizer, text)
        sentiment = self._safe_run(self.sentiment, text)
        fact_check = self._safe_run(
            self.fact_checker, text, context={"summary": summary.get("summary", "")}
        )

        return {
            "summary": summary,
            "sentiment": sentiment,
            "fact_check": fact_check,
        }

    @staticmethod
    def _safe_run(agent, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            return agent.process(text, context=context)
        except Exception as exc:
            logger.exception("Agent %s failed", agent.name)
            return {"error": f"{agent.name} agent failed: {exc}"}
