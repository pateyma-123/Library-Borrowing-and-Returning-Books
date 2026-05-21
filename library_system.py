# library_system.py
"""
Core Library Management Logic Module.

This module provides the `LibraryManager` class, which acts as the central
controller for the library's data. It manages the state of books (inventory)
and borrowing records (transactions).

Features:
    - Data Persistence: Automatically loads data from CSV files on initialization
      and saves changes immediately after operations.
    - Strategy Pattern: Implements flexible strategies for calculating fines
      and searching for books, allowing behavior to be changed at runtime.
      
Classes:
    LibraryManager: The main class for managing library operations.
"""

import csv
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from models import Book, BorrowRecord
from strategies import FineStrategy, StandardFineStrategy, SearchStrategy, TitleSearchStrategy


class LibraryManager:
    """
    Manages the library's state, including book inventory and borrowing records.
    
    This class is responsible for CRUD operations on books, handling borrowing
    and returning logic, and persisting data to CSV files.

    Attributes:
        name (str): The name of the library.
        books (Dict[str, Book]): A dictionary mapping ISBNs to Book objects.
        records (Dict[str, BorrowRecord]): A dictionary mapping Record IDs to BorrowRecord objects.
        record_counter (int): A counter to generate unique IDs for new borrow records.
    """

    def __init__(self, library_name: str = "Central Library", books_file: str = "books.csv",
                 history_file: str = "history.csv"):
        """
        Initialize the LibraryManager with data persistence settings.

        Args:
            library_name (str): The display name of the library. Defaults to "Central Library".
            books_file (str): The filename for storing book inventory data. Defaults to "books.csv".
            history_file (str): The filename for storing transaction history. Defaults to "history.csv".
        """
        self.name = library_name
        self.books: Dict[str, Book] = {}
        self.records: Dict[str, BorrowRecord] = {}
        self.record_counter = 0

        # Configuration for file storage
        self.books_file = books_file
        self.history_file = history_file

        # Initialize default strategies for fines and search
        self._fine_strategy: FineStrategy = StandardFineStrategy()
        self._search_strategy: SearchStrategy = TitleSearchStrategy()

        # Load existing data from CSV files upon instantiation
        self._load_data()

    # ----------------- Internal Data Handling Methods ----------------- #

    def _load_data(self):
        """
        Load books and records from CSV files into memory.
        
        This method checks if the CSV files exist. If they do, it reads them
        row by row, reconstructing Book and BorrowRecord objects.
        It also synchronizes the record_counter to ensure new IDs are unique.
        """
        # Load Books from CSV
        if os.path.exists(self.books_file):
            with open(self.books_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    book = Book.from_csv_row(row)
                    self.books[book.isbn] = book

        # Load History from CSV
        if os.path.exists(self.history_file):
            with open(self.history_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    record = BorrowRecord.from_csv_row(row)
                    self.records[record.record_id] = record

                    # Extract numeric part of record_id (e.g., "BR0001" -> 1)
                    # to ensure the counter continues from the highest existing ID.
                    record_num = int(record.record_id.replace("BR", ""))
                    if record_num > self.record_counter:
                        self.record_counter = record_num

    def _save_books(self):
        """
        Save the current state of the book inventory to the CSV file.
        
        This overwrites the existing file to ensure data consistency.
        """
        with open(self.books_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['isbn', 'title', 'author', 'publication', 'year', 'category', 
                          'total_copies', 'available_copies']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books.values():
                writer.writerow(book.to_dict())

    def _save_records(self):
        """
        Save the current borrowing records to the history CSV file.
        
        This overwrites the existing file.
        """
        with open(self.history_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['record_id', 'isbn', 'book_title', 'borrower_name', 'borrower_id', 
                          'borrow_date', 'due_date', 'return_date', 'is_returned']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records.values():
                writer.writerow(record.to_dict())

    # ----------------- Strategy Management Methods ----------------- #

    def set_fine_strategy(self, strategy: FineStrategy):
        """
        Set the strategy used for calculating fines.
        
        Args:
            strategy (FineStrategy): An instance of a FineStrategy subclass.
        """
        self._fine_strategy = strategy

    def set_search_strategy(self, strategy: SearchStrategy):
        """
        Set the strategy used for searching books.
        
        Args:
            strategy (SearchStrategy): An instance of a SearchStrategy subclass.
        """
        self._search_strategy = strategy

    # ----------------- Feature 1: Inventory Methods ----------------- #

    def add_book(self, isbn: str, title: str, author: str, publication: str, year: int, 
                 category: str, copies: int = 1) -> Tuple[bool, str]:
        """
        Add a new book to the inventory or update existing copies.
        
        If a book with the given ISBN already exists, its total copies are incremented.
        Otherwise, a new Book object is created.

        Args:
            isbn (str): The unique ISBN of the book.
            title (str): The book's title.
            author (str): The book's author.
            publication (str): The publisher name.
            year (int): The publication year.
            category (str): The genre or category.
            copies (int, optional): The number of copies to add. Defaults to 1.

        Returns:
            Tuple[bool, str]: A tuple containing the success status (True/False)
                              and a descriptive message string.
        """
        # Validate input
        if not all([isbn, title, author, publication, year]):
            return False, "All fields are required."

        if isbn in self.books:
            # Update existing book
            self.books[isbn].total_copies += copies
            self.books[isbn].available_copies += copies
            self._save_books()
            return True, f"Updated copies for '{title}'."
        
        # Create new book entry
        self.books[isbn] = Book(isbn, title, author, publication, year, category, copies, copies)
        self._save_books()
        return True, f"Book '{title}' added."

    def remove_book(self, isbn: str) -> Tuple[bool, str]:
        """
        Remove a book from the inventory.
        
        A book cannot be removed if some copies are currently borrowed.

        Args:
            isbn (str): The ISBN of the book to remove.

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if isbn not in self.books:
            return False, "Book not found."
        
        # Check if any copies are currently loaned out
        if self.books[isbn].available_copies < self.books[isbn].total_copies:
            return False, "Cannot remove, some copies are borrowed."

        del self.books[isbn]
        self._save_books()
        return True, "Book removed."

    def search_books(self, query: str) -> List[Book]:
        """
        Filter the inventory based on the current search strategy.
        
        Args:
            query (str): The search term.

        Returns:
            List[Book]: A list of books matching the query.
        """
        return self._search_strategy.filter(list(self.books.values()), query)

    def get_all_books(self) -> List[Book]:
        """
        Retrieve all books in the inventory.
        
        Returns:
            List[Book]: List of all Book objects.
        """
        return list(self.books.values())

    # ----------------- Feature 2: Borrowing Methods ----------------- #

    def borrow_book(self, isbn: str, borrower_name: str, borrower_id: str, days: int = 14) -> Tuple[bool, str]:
        """
        Register a new borrowing transaction.
        
        Decrements the available copies of the book and creates a BorrowRecord.

        Args:
            isbn (str): The ISBN of the book to borrow.
            borrower_name (str): Name of the borrower.
            borrower_id (str): ID of the borrower.
            days (int, optional): Duration of the loan in days. Defaults to 14.

        Returns:
            Tuple[bool, str]: Success status and message.
        """
        if isbn not in self.books:
            return False, "Book not found."

        book = self.books[isbn]
        if book.available_copies < 1:
            return False, "No copies available."

        # Generate a unique record ID
        self.record_counter += 1
        record_id = f"BR{self.record_counter:04d}"
        now = datetime.now()

        # Create the borrow record
        record = BorrowRecord(
            record_id=record_id,
            isbn=isbn,
            book_title=book.title,
            borrower_name=borrower_name,
            borrower_id=borrower_id,
            borrow_date=now,
            due_date=now + timedelta(days=days)
        )

        # Update book availability and save
        book.available_copies -= 1
        self.records[record_id] = record

        self._save_books()
        self._save_records()
        return True, f"Book borrowed successfully by {borrower_name}. Due: {record.due_date.strftime('%Y-%m-%d')}"

    def get_active_borrows(self) -> List[BorrowRecord]:
        """
        Retrieve all currently active (unreturned) borrow records.
        
        Returns:
            List[BorrowRecord]: List of active records.
        """
        return [r for r in self.records.values() if not r.is_returned]

    # ----------------- Feature 3: Returning Methods ----------------- #

    def return_book(self, record_id: str) -> Tuple[bool, str, float]:
        """
        Process the return of a borrowed book.
        
        Marks the record as returned, calculates fines if overdue,
        and increments the book's available copies.

        Args:
            record_id (str): The ID of the borrow record.

        Returns:
            Tuple[bool, str, float]: Success status, message, and calculated fine amount.
        """
        if record_id not in self.records:
            return False, "Record not found.", 0.0

        record = self.records[record_id]
        if record.is_returned:
            return False, "Book already returned.", 0.0

        # Update record status
        return_date = datetime.now()
        record.is_returned = True
        record.return_date = return_date

        # Calculate fine using the strategy pattern
        fine = self._fine_strategy.calculate(record.due_date, return_date)

        # Restore book availability
        if record.isbn in self.books:
            self.books[record.isbn].available_copies += 1

        self._save_books()
        self._save_records()
        return True, f"Book returned successfully.", fine

    def get_return_history(self) -> List[BorrowRecord]:
        """
        Retrieve the history of all returned books.
        
        Returns:
            List[BorrowRecord]: List of returned records.
        """
        return [r for r in self.records.values() if r.is_returned]

    def get_stats(self) -> dict:
        """
        Calculate and return summary statistics for the library.
        
        Returns:
            dict: Dictionary containing total_titles, total_copies, available_copies, etc.
        """
        total_books = sum(b.total_copies for b in self.books.values())
        available = sum(b.available_copies for b in self.books.values())
        return {
            "total_titles": len(self.books),
            "total_copies": total_books,
            "available_copies": available,
            "borrowed_copies": total_books - available
        }
