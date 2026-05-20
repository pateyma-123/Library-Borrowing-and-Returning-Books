# library_system.py
import csv
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from models import Book, BorrowRecord
from strategies import FineStrategy, StandardFineStrategy, SearchStrategy, TitleSearchStrategy


class LibraryManager:
    # Updated Init to accept filenames
    def __init__(self, library_name: str = "Central Library", books_file: str = "books.csv",
                 history_file: str = "history.csv"):
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
        self._fine_strategy = strategy

    def set_search_strategy(self, strategy: SearchStrategy):
        self._search_strategy = strategy

    # --- Feature 1: Book Inventory ---
    def add_book(self, isbn: str, title: str, author: str, publication: str, year: int, category: str,
                 copies: int = 1) -> Tuple[bool, str]:
        if not all([isbn, title, author, publication, year]):
            return False, "All fields are required."

        if isbn in self.books:
            self.books[isbn].total_copies += copies
            self.books[isbn].available_copies += copies
            self._save_books()  # SAVE CHANGES
            return True, f"Updated copies for '{title}'."

        self.books[isbn] = Book(isbn, title, author, publication, year, category, copies, copies)
        self._save_books()  # SAVE CHANGES
        return True, f"Book '{title}' added."

    def remove_book(self, isbn: str) -> Tuple[bool, str]:
        if isbn not in self.books:
            return False, "Book not found."
        if self.books[isbn].available_copies < self.books[isbn].total_copies:
            return False, "Cannot remove, some copies are borrowed."

        del self.books[isbn]
        self._save_books()  # SAVE CHANGES
        return True, "Book removed."

    def search_books(self, query: str) -> List[Book]:
        return self._search_strategy.filter(list(self.books.values()), query)

    def get_all_books(self) -> List[Book]:
        return list(self.books.values())

    # --- Feature 2: Book Borrowing ---
    def borrow_book(self, isbn: str, borrower_name: str, borrower_id: str, days: int = 14) -> Tuple[bool, str]:
        if isbn not in self.books:
            return False, "Book not found."

        book = self.books[isbn]
        if book.available_copies < 1:
            return False, "No copies available."

        self.record_counter += 1
        record_id = f"BR{self.record_counter:04d}"
        now = datetime.now()

        record = BorrowRecord(
            record_id=record_id,
            isbn=isbn,
            book_title=book.title,
            borrower_name=borrower_name,
            borrower_id=borrower_id,
            borrow_date=now,
            due_date=now + timedelta(days=days)
        )

        book.available_copies -= 1
        self.records[record_id] = record

        self._save_books()  # SAVE CHANGES
        self._save_records()  # SAVE CHANGES
        return True, f"Book borrowed successfully by {borrower_name}. Due: {record.due_date.strftime('%Y-%m-%d')}"

    def get_active_borrows(self) -> List[BorrowRecord]:
        return [r for r in self.records.values() if not r.is_returned]

    # --- Feature 3: Input & Returning ---
    def return_book(self, record_id: str) -> Tuple[bool, str, float]:
        if record_id not in self.records:
            return False, "Record not found.", 0.0

        record = self.records[record_id]
        if record.is_returned:
            return False, "Book already returned.", 0.0

        return_date = datetime.now()
        record.is_returned = True
        record.return_date = return_date

        fine = self._fine_strategy.calculate(record.due_date, return_date)

        if record.isbn in self.books:
            self.books[record.isbn].available_copies += 1

        self._save_books()  # SAVE CHANGES
        self._save_records()  # SAVE CHANGES
        return True, f"Book returned successfully.", fine

    def get_return_history(self) -> List[BorrowRecord]:
        return [r for r in self.records.values() if r.is_returned]

    def get_stats(self) -> dict:
        total_books = sum(b.total_copies for b in self.books.values())
        available = sum(b.available_copies for b in self.books.values())
        return {
            "total_titles": len(self.books),
            "total_copies": total_books,
            "available_copies": available,
            "borrowed_copies": total_books - available
        }