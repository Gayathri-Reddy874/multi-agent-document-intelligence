"""Unit tests for the deterministic parts of the system.

The summarizer and sentiment agents load large pretrained models, so they're
intentionally left out of this fast unit-test suite; in a real CI setup
they'd be covered by a separate, marked integration test (e.g.
`@pytest.mark.integration`) that only runs on demand.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.fact_checker import FactCheckerAgent


def test_fact_checker_flags_positive_language():
    agent = FactCheckerAgent()
    result = agent.process("The system is operational. No issues detected.")
    assert result["verdict"] == "Consistent Positive Report"


def test_fact_checker_flags_risk_language():
    agent = FactCheckerAgent()
    result = agent.process("There was a problem. Latency was noisy throughout.")
    assert result["verdict"] == "Mixed / Risk Indicators Present"


def test_fact_checker_handles_empty_input():
    agent = FactCheckerAgent()
    result = agent.process("")
    assert result["verdict"] == "No Content"


def test_fact_checker_sentence_split_handles_no_trailing_period():
    agent = FactCheckerAgent()
    # Regression test: the original `.split(".")` implementation would still
    # catch this, but a real sentence tokenizer needs to handle "!" and "?"
    # and text without a trailing period without dropping the last sentence.
    result = agent.process("Great performance overall! Everything is operational")
    assert result["analysis"] == "Positive=2, Negative=0"

