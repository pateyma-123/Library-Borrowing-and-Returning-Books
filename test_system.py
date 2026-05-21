# test_system.py
"""
Unit Tests for the Library Management System.

This module contains pytest tests to verify the functionality of the
library system components, including models, strategies, and the
core LibraryManager class.

It ensures data integrity, correct behavior of business logic,
and data persistence.

Fixtures:
    library: Provides a clean LibraryManager instance for each test.
"""

import pytest
import os
from datetime import datetime, timedelta
from models import Book, BorrowRecord
from strategies import StandardFineStrategy
from library_system import LibraryManager


# ---------- Model Tests ----------
def test_book_creation():
    """
    Test the initialization and default values of the Book dataclass.
    
    Verifies that a Book object is created with the correct attributes
    and that `available_copies` defaults to `total_copies`.
    """
    book = Book(
        isbn="123", 
        title="Python 101", 
        author="Guido", 
        publication="Pearson", 
        year=2020, 
        category="Tech",
        total_copies=5
    )
    assert book.title == "Python 101"
    assert book.year == 2020
    assert book.available_copies == 5, "Available copies should default to total copies"


def test_borrow_record_creation():
    """
    Test the initialization of the BorrowRecord dataclass.
    
    Verifies that a new record is correctly marked as not returned.
    """
    now = datetime.now()
    record = BorrowRecord(
        record_id="BR01", 
        isbn="123", 
        book_title="PyBook", 
        borrower_name="Alice", 
        borrower_id="ID01", 
        borrow_date=now, 
        due_date=now
    )
    assert record.is_returned is False, "New records should not be marked as returned"


# ---------- Strategy Tests ----------
def test_standard_fine_strategy():
    """
    Test the StandardFineStrategy logic.
    
    Verifies that a fine is correctly calculated for books returned late.
    """
    strategy = StandardFineStrategy()
    due = datetime.now() - timedelta(days=2)  # 2 days late
    ret = datetime.now()
    
    # Expected: 2 days * 0.50 = 1.0
    assert strategy.calculate(due, ret) == 1.0


# ---------- Library System Tests ----------
@pytest.fixture
def library():
    """
    Pytest fixture to create a fresh LibraryManager instance.
    
    Uses separate test CSV files to avoid polluting production data.
    Handles setup (cleaning old files) and teardown (cleaning generated files).
    """
    # Define test file names
    test_books_file = "test_books.csv"
    test_history_file = "test_history.csv"

    # Teardown: Remove test files if they exist from previous runs
    if os.path.exists(test_books_file):
        os.remove(test_books_file)
    if os.path.exists(test_history_file):
        os.remove(test_history_file)

    # Setup: Create library instance with test files
    lib = LibraryManager("Test Library", books_file=test_books_file, history_file=test_history_file)

    # Add sample data for tests
    lib.add_book("111", "Flask Web", "A", "O'Reilly", 2022, "Tech", 2)
    lib.add_book("222", "Django", "B", "Packt", 2021, "Tech", 1)

    # Yield the library object to the test
    yield lib

    # Teardown: Clean up test files after the test finishes
    if os.path.exists(test_books_file):
        os.remove(test_books_file)
    if os.path.exists(test_history_file):
        os.remove(test_history_file)


def test_add_book(library):
    """
    Test that adding a book updates the library inventory correctly.
    """
    assert len(library.books) == 2
    assert library.books["111"].publication == "O'Reilly"


def test_borrow_book_success(library):
    """
    Test the happy path for borrowing a book.
    
    Verifies that borrowing a book decreases the available count.
    """
    success, msg = library.borrow_book("111", "John", "STU01")
    assert success is True
    assert library.books["111"].available_copies == 1


def test_return_book(library):
    """
    Test the book return process.
    
    Verifies that returning a book restores the available count.
    """
    # First, borrow a book
    library.borrow_book("111", "John", "STU01")
    record_id = list(library.records.keys())[0]

    # Now, return it
    success, msg, fine = library.return_book(record_id)
    assert success is True
    # Available copies should be restored to original count (2)
    assert library.books["111"].available_copies == 2


def test_persistence(library):
    """
    Test that data persists across library instance reboots.
    
    Simulates restarting the application by creating a new LibraryManager
    instance pointing to the same CSV files.
    """
    # Borrow a book to change state
    library.borrow_book("111", "Alice", "ID001")

    # Create a new library instance simulating a reboot
    new_lib = LibraryManager("Test Library", books_file="test_books.csv", history_file="test_history.csv")

    # Verify data persisted
    assert len(new_lib.books) == 2
    # Check that the book is still marked as borrowed (1 copy left)
    assert new_lib.books["111"].available_copies == 1
    # Check that the active borrow record exists
    assert len(new_lib.get_active_borrows()) == 1
