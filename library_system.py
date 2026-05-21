# library_system.py
"""
Core Library Management Logic.

This module contains the LibraryManager class which orchestrates
book inventory, borrowing operations, and data persistence via CSV files.
"""

import csv
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from models import Book, BorrowRecord
from strategies import FineStrategy, StandardFineStrategy, SearchStrategy, TitleSearchStrategy


class LibraryManager:
    """
    Manages the library's state, including books and borrowing records.

    Attributes:
        name (str): Name of the library.
        books (Dict[str, Book]): Dictionary of ISBN to Book objects.
        records (Dict[str, BorrowRecord]): Dictionary of Record IDs to BorrowRecord objects.
    """

    def __init__(self, library_name: str = "Central Library", books_file: str = "books.csv",
                 history_file: str = "history.csv"):
        """
        Initialize the LibraryManager.

        Args:
            library_name (str): Name of the library.
            books_file (str): Filename for storing book data.
            history_file (str): Filename for storing transaction history.
        """
        self.name = library_name
        self.books: Dict[str, Book] = {}
        self.records: Dict[str, BorrowRecord] = {}
        self.record_counter = 0

        # File names for persistence
        self.books_file = books_file
        self.history_file = history_file

        # Default strategies
        self._fine_strategy: FineStrategy = StandardFineStrategy()
        self._search_strategy: SearchStrategy = TitleSearchStrategy()

        # LOAD DATA AUTOMATICALLY ON START
        self._load_data()

    # --- Internal CSV Methods ---

    def _load_data(self):
        """Load books and records from CSV files if they exist."""
        # Load Books
        if os.path.exists(self.books_file):
            with open(self.books_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    book = Book.from_csv_row(row)
                    self.books[book.isbn] = book

        # Load History
        if os.path.exists(self.history_file):
            with open(self.history_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    record = BorrowRecord.from_csv_row(row)
                    self.records[record.record_id] = record

                    # Update counter to prevent duplicate IDs
                    record_num = int(record.record_id.replace("BR", ""))
                    if record_num > self.record_counter:
                        self.record_counter = record_num

    def _save_books(self):
        """Save current book inventory to CSV."""
        with open(self.books_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['isbn', 'title', 'author', 'publication', 'year', 'category', 'total_copies',
                          'available_copies']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books.values():
                writer.writerow(book.to_dict())

    def _save_records(self):
        """Save current borrow records to CSV."""
        with open(self.history_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['record_id', 'isbn', 'book_title', 'borrower_name', 'borrower_id', 'borrow_date', 'due_date',
                          'return_date', 'is_returned']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records.values():
                writer.writerow(record.to_dict())

    # --- Strategy Setters ---
    def set_fine_strategy(self, strategy: FineStrategy):
        """Set the strategy for calculating fines."""
        self._fine_strategy = strategy

    def set_search_strategy(self, strategy: SearchStrategy):
        """Set the strategy for searching books."""
        self._search_strategy = strategy

    # --- Feature 1: Book Inventory ---
    def add_book(self, isbn: str, title: str, author: str, publication: str, year: int, category: str,
                 copies: int = 1) -> Tuple[bool, str]:
        """
        Add a new book or update existing copies.

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if not all([isbn, title, author, publication, year]):
            return False, "All fields are required."

        if isbn in self.books:
            self.books[isbn].total_copies += copies
            self.books[isbn].available_copies += copies
            self._save_books()
            return True, f"Updated copies for '{title}'."

        self.books[isbn] = Book(isbn, title, author, publication, year, category, copies, copies)
        self._save_books()
        return True, f"Book '{