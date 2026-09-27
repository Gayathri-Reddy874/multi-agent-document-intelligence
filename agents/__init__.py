"""Agent implementations for the multi-agent document analysis system.

Intentionally does NOT eagerly import every agent here: SummarizerAgent and
SentimentAgent pull in `transformers`/`torch`, which are heavy and not
needed for pure-logic unit tests (e.g. of FactCheckerAgent). Import the
specific agent you need directly, e.g. `from agents.fact_checker import
FactCheckerAgent`.
"""
