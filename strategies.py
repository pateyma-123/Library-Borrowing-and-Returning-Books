"""
Strategy Patterns for Library Operations.

This module implements the Strategy design pattern for two key operations:
1. Fine Calculation: Different algorithms for computing overdue fines
2. Book Search: Different search methods (by title, by author, etc.)

By using strategies, the library system can easily switch between different
implementations without modifying core logic.

Classes:
    FineStrategy (ABC): Abstract base for fine calculation strategies
    StandardFineStrategy: Concrete fine calculation ($0.50/day overdue)
    SearchStrategy (ABC): Abstract base for search strategies
    TitleSearchStrategy: Search books by title (case-insensitive)
    AuthorSearchStrategy: Search books by author (case-insensitive)

Author: Library Management Team
Version: 1.0
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models import Book


class FineStrategy(ABC):
    """
    Abstract base class for fine calculation strategies.

    Defines the interface that all fine calculation strategies must implement.
    This allows the library to support different fine policies without
    modifying the core library logic.
    """

    @abstractmethod
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """
        Calculate the fine amount based on due and return dates.

        Args:
            due_date (datetime): The date the book was due
            return_date (datetime): The actual date the book was returned

        Returns:
            float: Fine amount in dollars. Returns 0.0 if not overdue.
        """
        pass


class StandardFineStrategy(FineStrategy):
    """
    Concrete strategy for standard fine calculation.

    Implements a simple flat-rate fine: $0.50 per day overdue.
    No fine is charged if the book is returned on or before the due date.
    """

    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """
        Calculate fine based on days overdue.

        Args:
            due_date (datetime): The date the book was due
            return_date (datetime): The actual date the book was returned

        Returns:
            float: Fine amount ($0.50 per day overdue). Returns 0.0 if on time.

        Example:
            - Book due on Jan 1, returned on Jan 3 → 2 days × $0.50 = $1.00
            - Book due on Jan 1, returned on Jan 1 → 0 days × $0.50 = $0.00
        """
        if return_date <= due_date:
            return 0.0
        overdue_days = (return_date - due_date).days
        return overdue_days * 0.50


class SearchStrategy(ABC):
    """
    Abstract base class for search/filter strategies.

    Defines the interface that all search strategies must implement.
    This allows the library to support multiple search methods without
    modifying the core library logic.
    """

    @abstractmethod
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filter a list of books based on a search query.

        Args:
            books (List[Book]): List of Book objects to search
            query (str): Search query string

        Returns:
            List[Book]: Filtered list of matching books
        """
        pass


class TitleSearchStrategy(SearchStrategy):
    """
    Concrete strategy to search books by title.

    Performs case-insensitive substring matching on book titles.
    """

    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filter books where the title contains the query string.

        Args:
            books (List[Book]): List of books to filter
            query (str): Title substring to search for

        Returns:
            List[Book]: Books whose title contains the query (case-insensitive)

        Example:
            - Query: "python"
            - Matches: "Python 101", "Advanced Python", "Python Crash Course"
        """
        query = query.lower()
        return [b for b in books if query in b.title.lower()]


class AuthorSearchStrategy(SearchStrategy):
    """
    Concrete strategy to search books by author.

    Performs case-insensitive substring matching on author names.
    """

    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filter books where the author name contains the query string.

        Args:
            books (List[Book]): List of books to filter
            query (str): Author name substring to search for

        Returns:
            List[Book]: Books whose author contains the query (case-insensitive)

        Example:
            - Query: "ramalho"
            - Matches: "Fluent Python" by Luciano Ramalho
        """
        query = query.lower()
        return [b for b in books if query in b.author.lower()]
