# strategies.py
"""
Strategy Patterns for Library Operations.

This module implements the Strategy Design Pattern to encapsulate interchangeable
algorithms. Specifically, it defines strategies for calculating overdue fines
and filtering (searching) the book inventory.

The Strategy Pattern allows the LibraryManager to change behavior (e.g., switching
from a standard fine calculation to a premium one) at runtime without changing
its core code.

Classes:
    FineStrategy (ABC): Abstract base for fine calculation.
    StandardFineStrategy: Calculates fines based on a daily rate.
    SearchStrategy (ABC): Abstract base for searching.
    TitleSearchStrategy: Filters books by title.
    AuthorSearchStrategy: Filters books by author.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, TYPE_CHECKING

# Avoid circular imports by using TYPE_CHECKING
if TYPE_CHECKING:
    from models import Book


class FineStrategy(ABC):
    """
    Abstract Base Class for fine calculation strategies.
    
    Subclasses must implement the `calculate` method to define specific
    fine logic.
    """
    
    @abstractmethod
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """
        Calculate the fine amount based on the due date and return date.
        
        Args:
            due_date (datetime): The date the book was due.
            return_date (datetime): The actual date the book was returned.

        Returns:
            float: The calculated fine amount in currency units.
        """
        pass


class StandardFineStrategy(FineStrategy):
    """
    A concrete strategy for calculating standard library fines.
    
    This strategy charges a fixed rate for every day a book is overdue.
    """
    
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        """
        Calculates fine based on a daily rate of 0.50.
        
        If the book is returned on or before the due date, the fine is 0.
        
        Args:
            due_date (datetime): The due date.
            return_date (datetime): The return date.

        Returns:
            float: The total fine amount.
        """
        if return_date <= due_date:
            return 0.0
        
        # Calculate the number of days late
        overdue_days = (return_date - due_date).days
        
        # Rate: $0.50 per day
        return overdue_days * 0.50


class SearchStrategy(ABC):
    """
    Abstract Base Class for book search/filter strategies.
    
    Subclasses must implement the `filter` method to define how the
    book list is filtered.
    """
    
    @abstractmethod
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filter a list of books based on a search query.
        
        Args:
            books (List[Book]): The list of books to filter.
            query (str): The search term.

        Returns:
            List[Book]: A filtered list of books matching the criteria.
        """
        pass


class TitleSearchStrategy(SearchStrategy):
    """
    Concrete strategy to search books by their title.
    
    Performs a case-insensitive substring match against the book's title.
    """
    
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filters books where the title contains the query string.
        
        Args:
            books (List[Book]): List of books.
            query (str): Search string.

        Returns:
            List[Book]: Filtered list.
        """
        query = query.lower()
        return [b for b in books if query in b.title.lower()]


class AuthorSearchStrategy(SearchStrategy):
    """
    Concrete strategy to search books by their author.
    
    Performs a case-insensitive substring match against the author's name.
    """
    
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        """
        Filters books where the author name contains the query string.
        
        Args:
            books (List[Book]): List of books.
            query (str): Search string.

        Returns:
            List[Book]: Filtered list.
        """
        query = query.lower()
        return [b for b in books if query in b.author.lower()]
