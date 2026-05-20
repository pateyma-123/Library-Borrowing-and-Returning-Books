# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Represents a book entity in the library."""
    isbn: str
    title: str
    author: str
    publication: str
    year: int
    category: str
    total_copies: int = 1
    available_copies: Optional[int] = None
    date_added: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.available_copies is None:
            self.available_copies = self.total_copies

    def to_dict(self) -> dict:
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publication": self.publication,
            "year": self.year,
            "category": self.category,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies
        }

    @classmethod
    def from_csv_row(cls, row: dict) -> 'Book':
        """Create a Book object from a CSV dictionary row."""
        return cls(
            isbn=row['isbn'],
            title=row['title'],
            author=row['author'],
            publication=row['publication'],
            year=int(row['year']),
            category=row['category'],
            total_copies=int(row['total_copies']),
            available_copies=int(row['available_copies'])
        )


@dataclass
class BorrowRecord:
    """Represents a transaction record for a borrowed book."""
    record_id: str
    isbn: str
    book_title: str
    borrower_name: str
    borrower_id: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    is_returned: bool = False

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "isbn": self.isbn,
            "book_title": self.book_title,
            "borrower_name": self.borrower_name,
            "borrower_id": self.borrower_id,
            "borrow_date": self.borrow_date.strftime("%Y-%m-%d"),
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "return_date": self.return_date.strftime("%Y-%m-%d") if self.return_date else "",
            "is_returned": str(self.is_returned)
        }

    @classmethod
    def from_csv_row(cls, row: dict) -> 'BorrowRecord':
        """Create a BorrowRecord object from a CSV dictionary row."""
        return cls(
            record_id=row['record_id'],
            isbn=row['isbn'],
            book_title=row['book_title'],
            borrower_name=row['borrower_name'],
            borrower_id=row['borrower_id'],
            borrow_date=datetime.strptime(row['borrow_date'], "%Y-%m-%d"),
            due_date=datetime.strptime(row['due_date'], "%Y-%m-%d"),
            return_date=datetime.strptime(row['return_date'], "%Y-%m-%d") if row['return_date'] else None,
            is_returned=row['is_returned'].lower() == 'true'
        )