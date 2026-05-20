# test_system.py
import pytest
import os
from datetime import datetime, timedelta
from models import Book, BorrowRecord
from strategies import StandardFineStrategy
from library_system import LibraryManager


# ---------- Model Tests ----------
def test_book_creation():
    book = Book(isbn="123", title="Python 101", author="Guido", publication="Pearson", year=2020, category="Tech",
                total_copies=5)
    assert book.title == "Python 101"
    assert book.year == 2020
    assert book.available_copies == 5


def test_borrow_record_creation():
    now = datetime.now()
    record = BorrowRecord("BR01", "123", "PyBook", "Alice", "ID01", now, now)
    assert record.is_returned is False


# ---------- Strategy Tests ----------
def test_standard_fine_strategy():
    strategy = StandardFineStrategy()
    due = datetime.now() - timedelta(days=2)
    ret = datetime.now()
    assert strategy.calculate(due, ret) == 1.0


# ---------- Library System Tests ----------
@pytest.fixture
def library():
    # Define test file names
    test_books_file = "test_books.csv"
    test_history_file = "test_history.csv"

    # Clean up test files BEFORE tests run to ensure a clean state
    if os.path.exists(test_books_file):
        os.remove(test_books_file)
    if os.path.exists(test_history_file):
        os.remove(test_history_file)

    # Create library with TEST FILES
    lib = LibraryManager("Test Library", books_file=test_books_file, history_file=test_history_file)

    # Add sample data for tests
    lib.add_book("111", "Flask Web", "A", "O'Reilly", 2022, "Tech", 2)
    lib.add_book("222", "Django", "B", "Packt", 2021, "Tech", 1)

    # Provide the library object to the test
    yield lib

    # Clean up test files AFTER tests run
    if os.path.exists(test_books_file):
        os.remove(test_books_file)
    if os.path.exists(test_history_file):
        os.remove(test_history_file)


def test_add_book(library):
    assert len(library.books) == 2
    assert library.books["111"].publication == "O'Reilly"


def test_borrow_book_success(library):
    success, msg = library.borrow_book("111", "John", "STU01")
    assert success
    assert library.books["111"].available_copies == 1


def test_return_book(library):
    library.borrow_book("111", "John", "STU01")
    record_id = list(library.records.keys())[0]

    success, msg, fine = library.return_book(record_id)
    assert success
    assert library.books["111"].available_copies == 2  # Restored


def test_persistence(library):
    # Borrow a book
    library.borrow_book("111", "Alice", "ID001")

    # Create a new library instance pointing to the SAME TEST FILES
    # This simulates restarting the application
    new_lib = LibraryManager("Test Library", books_file="test_books.csv", history_file="test_history.csv")

    # Check if data persisted
    assert len(new_lib.books) == 2
    assert new_lib.books["111"].available_copies == 1
    assert len(new_lib.get_active_borrows()) == 1