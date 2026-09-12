from abc import ABC, abstractmethod
from typing import Any


class BaseDBManager(ABC):
    """Abstract base class for DB managers."""

    @abstractmethod
    def execute_query(self, query: str, **kwargs) -> bool:
        """Execute a modifying query (INSERT/UPDATE/DELETE)."""

    @abstractmethod
    def execute_fetch(self, query: str, **kwargs) -> Any:
        """Execute a SELECT and return results."""

    def transaction(self):
        """Optional transaction context manager; adapters may override."""
        raise NotImplementedError()
