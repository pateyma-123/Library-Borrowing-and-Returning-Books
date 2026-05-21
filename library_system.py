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

    The LibraryManager acts as the central controller for the application.
    It handles data persistence, enforces business rules for borrowing/returning,
    and allows for strategy injection for search and fine calculation.

    Attributes:
        name (str): The name of the library instance.
        books (Dict[str, Book]): A mapping of ISBN strings to Book objects.
        records (Dict[str, BorrowRecord]): A mapping of Record IDs to BorrowRecord objects.
        books_file (str): The file path for book inventory persistence.
        history_file (str): The file path for transaction history persistence.
    """

    def __init__(self, library_name: str = "Central Library", books_file: str = "books.csv",
                 history_file: str = "history.csv"):
        """
        Initialize the LibraryManager with configuration and load data.

        Args:
            library_name (str): The display name of the library. Defaults to "Central Library".
            books_file (str): Path to the CSV file for book storage. Defaults to "books.csv".
            history_file (str): Path to the CSV file for borrow records. Defaults to "history.csv".
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
        """
        Load books and records from CSV files if they exist.

        This method is called during initialization to restore state.
        It reads 'books.csv' and 'history.csv' and populates the internal
        dictionaries. It also adjusts the record_counter to prevent ID collisions.
        """
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
                    try:
                        record_num = int(record.record_id.replace("BR", ""))
                        if record_num > self.record_counter:
                            self.record_counter = record_num
                    except ValueError:
                        pass # Handle legacy or malformed IDs gracefully

    def _save_books(self):
        """
        Persist the current book inventory to the CSV file.

        Overwrites the existing books file with the current state of self.books.
        """
        with open(self.books_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['isbn', 'title', 'author', 'publication', 'year', 'category', 'total_copies',
                          'available_copies']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books.values():
                writer.writerow(book.to_dict())

    def _save_records(self):
        """
        Persist the current borrow records to the CSV file.

        Overwrites the existing history file with the current state of self.records.
        """
        with open(self.history_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['record_id', 'isbn', 'book_title', 'borrower_name', 'borrower_id', 'borrow_date', 'due_date',
                          'return_date', 'is_returned']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records.values():
                writer.writerow(record.to_dict())

    # --- Strategy Se