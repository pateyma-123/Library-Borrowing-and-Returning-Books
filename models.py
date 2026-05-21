"""
Data Models for Library System.

This module defines the core data structures for the library management system
using Python dataclasses. It handles serialization/deserialization to/from
dictionaries for CSV file storage and retrieval.

Classes:
    Book: Represents a book entity with inventory information
    BorrowRecord: Represents a transaction record for a borrowed book

Author: Library Management Team
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """
    Represents a book entity in the library.

    Attributes:
        isbn (str): Unique International Standard Book Number (ISBN-13)
        title (str): Title of the book
        author (str): Name of the author
        publication (str): Name of the publisher
        year (int): Year of publication
        category (str): Book category or genre (e.g., 'Fiction', 'Programming')
        total_copies (int): Total number of physical copies owned by library
        available_copies (int): Number of copies currently available for borrowing
        date_added (datetime): Timestamp when book was added to inventory

    Methods:
        __post_init__(): Initialize available_copies if not explicitly set
        to_dict(): Convert object to dictionary for CSV export
        from_csv_row(): Class method to create Book from CSV row dictionary
    """
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
        """
        Initialize available_copies to total_copies if not provided.

        This ensures that when a new book is added, the available count
        matches the total count until borrows reduce the available amount.
        """
        if self.available_copies is None:
            self.available_copies = self.total_copies

    def to_dict(self) -> dict:
        """
        Convert the Book object to a dictionary for CSV serialization.

        Returns:
            dict: Dictionary with keys matching CSV column headers
        """
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
        """
        Create a Book object from a CSV dictionary row.

        Args:
            row (dict): Dictionary from CSV reader with book data

        Returns:
            Book: New Book instance with data from CSV
        """
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
    """
    Represents a transaction record for a borrowed book.

    Each record tracks a single borrowing transaction from start to completion,
    including borrower information, dates, and return status.

    Attributes:
        record_id (str): Unique identifier for this transaction (e.g., 'BR001')
        isbn (str): ISBN of the borrowed book
        book_title (str): Title of the borrowed book (cached for history)
        borrower_name (str): Full name of the person borrowing the book
        borrower_id (str): Student ID or Staff ID of the borrower
        borrow_date (datetime): Date when book was borrowed
        due_date (datetime): Date when book must be returned
        return_date (datetime): Actual date when book was returned (None if not yet returned)
        is_returned (bool): Flag indicating if the book has been returned

    Methods:
        to_dict(): Convert object to dictionary for CSV export
        from_csv_row(): Class method to create BorrowRecord from CSV row dictionary
    """
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
        """
        Convert the BorrowRecord object to a dictionary for CSV serialization.

        Dates are formatted as YYYY-MM-DD strings for CSV compatibility.

        Returns:
            dict: Dictionary with keys matching CSV column headers
        """
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
        """
        Create a BorrowRecord object from a CSV dictionary row.

        Parses string dates back into datetime objects.

        Args:
            row (dict): Dictionary from CSV reader with record data

        Returns:
            BorrowRecord: New BorrowRecord instance with data from CSV
        """
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
