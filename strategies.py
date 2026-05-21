# strategies.py
"""
Strategy Patterns for Library Operations.

This module defines abstract base classes and concrete implementations
for searching books and calculating fines.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models import Book

class FineStrategy(ABC):
    """Abstract base class for fine calculation strategies."""
    
    @abstractmethod
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """Calculate the fine amount based on dates."""
        pass

class StandardFineStrategy(FineStrategy):
    """Concrete strategy for standard fine calculation (e.g., $0.50 per day)."""
    
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """
        Calculates fine. Returns 0.0 if not overdue.
        Fine rate: 0.50 per day overdue.
        """
        if return_date <= due_date:
            return 0.0
        overdue_days = (return_date - due_date).days
        return overdue_days * 0.50

class SearchStrategy(ABC):
    """Abstract base class for search/filter strategies."""
    
    @abstractmethod
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """Filter a list of books based on a query."""
        pass

class TitleSearchStrategy(SearchStrategy):
    """Concrete strategy to search books by title."""
    
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """Filters books where the title contains the query string (case-insensitive)."""
        query = query.lower()
        return [b for b in books if query in b.title.lower()]

class AuthorSearchStrategy(SearchStrategy):
    """Concrete strategy to search books by author."""
    
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """Filters books where the author name contains the query string (case-insensitive)."""
        query = query.lower()
        return [b for b in books if query in b.author.lower()]
