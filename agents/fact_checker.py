"""Heuristic consistency-checking agent.

Honest naming note: this agent does NOT verify facts against any external
source of truth. It's a keyword-based heuristic that flags whether a
document's language leans toward positive/operational phrasing or toward
risk-indicating phrasing (problems, latency, etc.). It's kept as
"FactCheckerAgent" for backward compatibility with the rest of the pipeline,
but the README and docstrings are explicit about what it actually does so
it isn't mistaken for real fact verification.
"""

import re
from typing import Any, Dict, List, Optional

import config
from .base_agent import BaseAgent


class FactCheckerAgent(BaseAgent):
    """Scores text as positive / mixed / neutral based on keyword heuristics."""

    def __init__(self) -> None:
        super().__init__("FactChecker")

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        # Splits on ., !, or ? followed by whitespace — more robust than a
        # bare `.split(".")`, which breaks on abbreviations and mangles the
        # last sentence when the text lacks a trailing period.
        return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]

    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"verdict": "No Content", "evidence": "", "analysis": "Positive=0, Negative=0"}

        summary = (context or {}).get("summary", "")
        sentences = self._split_sentences(text)

        positive = 0
        negative = 0

        for sentence in sentences:
            lowered = sentence.lower()
            if any(word in lowered for word in config.POSITIVE_KEYWORDS):
                positive += 1
            if any(word in lowered for word in config.NEGATIVE_KEYWORDS):
                negative += 1

        if positive > negative:
            verdict = "Consistent Positive Report"
        elif negative > positive:
            verdict = "Mixed / Risk Indicators Present"
        else:
            verdict = "Neutral Technical Report"

        return {
            "verdict": verdict,
            "evidence": summary[:200] if summary else text[:200],
            "analysis": f"Positive={positive}, Negative={negative}",
        }


