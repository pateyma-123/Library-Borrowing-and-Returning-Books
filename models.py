# models.py
"""
Data Models for Library System Entities.

This module defines the core data structures used throughout the application.
It utilizes Python's `dataclasses` to reduce boilerplate code for initializing
and representing objects.

Classes:
    Book: Represents a physical book item in the inventory.
    BorrowRecord: Represents a transaction where a book is borrowed.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """
    Represents a book entity within the library system.
    
    A Book object stores metadata about the book as well as inventory counts.
    It is uniquely identified by its ISBN.

    Attributes:
        isbn (str): The International Standard Book Number (Unique ID).
        title (str): The title of the book.
        author (str): The author of the book.
        publication (str): The name of the publishing company.
        year (int): The year the book was published.
        category (str): The genre or classification of the book.
        total_copies (int): The total number of copies owned by the library. Defaults to 1.
        available_copies (Optional[int]): The number of copies currently available for borrowing.
                                          Defaults to match `total_copies` if not provided.
        date_added (datetime): Timestamp of when the book was added to the system.
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
        Post-initialization hook.
        
        Ensures that `available_copies` is set to `total_copies` if it was not
        explicitly provided during initialization.
        """
        if self.available_copies is None:
            self.available_copies = self.total_copies

    def to_dict(self) -> dict:
        """
        Serialize the Book object to a dictionary.
        
        This method is used for CSV export. It excludes non-serializable objects
        like `date_added` if they are not needed in the persistent storage.

        Returns:
            dict: A dictionary representation of the book's data.
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
        Factory method to create a Book instance from a CSV row dictionary.
        
        Args:
            row (dict): A dictionary representing a row from the CSV file.

        Returns:
            Book: A new Book instance populated with the row data.
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
    
    This class tracks who borrowed the book, when it was borrowed, and its return status.

    Attributes:
        record_id (str): A unique identifier for this transaction (e.g., "BR0001").
        isbn (str): The ISBN of the borrowed book.
        book_title (str): A snapshot of the book's title at the time of borrowing.
        borrower_name (str): Name of the person borrowing the book.
        borrower_id (str): ID of the person borrowing the book.
        borrow_date (datetime): Timestamp when the book was borrowed.
        due_date (datetime): Timestamp when the book is expected to be returned.
        return_date (Optional[datetime]): Timestamp when the book was actually returned.
                                          None if the book has not been returned yet.
        is_returned (bool): Flag indicating if the book has been returned. Defaults to False.
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
        Serialize the BorrowRecord object to a dictionary for CSV storage.

        Returns:
            dict: A dictionary representation of the record.
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
        Factory method to create a BorrowRecord instance from a CSV row dictionary.
        
        Args:
            row (dict): A dictionary representing a row from the history CSV file.

        Returns:
            BorrowRecord: A new BorrowRecord instance.
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
