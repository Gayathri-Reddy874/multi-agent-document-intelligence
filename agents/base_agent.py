"""Abstract base class that every agent in the system must implement."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAgent(ABC):
    """Common interface for all agents.

    Subclasses must implement `process`, which takes the raw document text
    and an optional context dict (used for passing data between agents,
    e.g. a summary produced earlier in the pipeline) and returns a
    JSON-serializable dict of results.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def process(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the agent's analysis on `text` and return a results dict."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
