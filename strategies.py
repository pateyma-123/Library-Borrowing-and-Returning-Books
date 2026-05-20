# strategies.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models import Book

class FineStrategy(ABC):
    @abstractmethod
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        pass

class StandardFineStrategy(FineStrategy):
    def calculate(self, due_date: datetime, return_date: datetime) -> float:
        if return_date <= due_date:
            return 0.0
        overdue_days = (return_date - due_date).days
        return overdue_days * 0.50

class SearchStrategy(ABC):
    @abstractmethod
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        pass

class TitleSearchStrategy(SearchStrategy):
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        query = query.lower()
        return [b for b in books if query in b.title.lower()]

class AuthorSearchStrategy(SearchStrategy):
    def filter(self, books: List['Book'], query: str) -> List['Book']:
        query = query.lower()
        return [b for b in books if query in b.author.lower()]