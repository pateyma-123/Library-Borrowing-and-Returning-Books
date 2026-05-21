"""
Utility Functions for Library Management System.

This module provides helper functions used throughout the library system
for common operations like date formatting, validation, and data processing.

Functions:
    format_date(dt): Convert datetime to readable string format
    is_valid_isbn(isbn): Validate ISBN format
    calculate_days_until_due(due_date): Calculate remaining days until due
    validate_book_data(data): Validate book information before adding to inventory
    get_overdue_books(records): Filter overdue books from borrow records

Author: Library Management Team
Version: 1.0
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional
from models import BorrowRecord


def format_date(dt: datetime) -> str:
    """
    Convert datetime object to human-readable date string.

    Args:
        dt (datetime): Datetime object to format

    Returns:
        str: Formatted date string in 'YYYY-MM-DD' format

    Example:
        >>> format_date(datetime(2024, 1, 15))
        '2024-01-15'
    """
    if dt is None:
        return "N/A"
    return dt.strftime('%Y-%m-%d')


def is_valid_isbn(isbn: str) -> bool:
    """
    Validate ISBN format (basic validation).

    Checks:
    - ISBN is not empty
    - ISBN contains only digits and hyphens
    - ISBN length is reasonable (10 or 13 digits)

    Args:
        isbn (str): ISBN string to validate

    Returns:
        bool: True if ISBN format appears valid, False otherwise

    Example:
        >>> is_valid_isbn('978-0134685991')
        True
        >>> is_valid_isbn('')
        False
    """
    if not isbn or not isinstance(isbn, str):
        return False
    
    # Remove hyphens for digit check
    isbn_digits = isbn.replace('-', '')
    
    # Check if contains only digits
    if not isbn_digits.isdigit():
        return False
    
    # Valid ISBNs are 10 or 13 digits
    return len(isbn_digits) in [10, 13]


def calculate_days_until_due(due_date: datetime) -> int:
    """
    Calculate the number of days remaining until the due date.

    Args:
        due_date (datetime): The due date to calculate from

    Returns:
        int: Number of days remaining (negative if overdue)

    Example:
        >>> calculate_days_until_due(datetime.now() + timedelta(days=5))
        5
        >>> calculate_days_until_due(datetime.now() - timedelta(days=2))
        -2
    """
    if due_date is None:
        return 0
    
    delta = due_date - datetime.now()
    return delta.days


def validate_book_data(data: Dict) -> Tuple[bool, str]:
    """
    Validate book information before adding to inventory.

    Checks:
    - All required fields are present
    - ISBN is valid format
    - Year is a reasonable number
    - Copies count is positive

    Args:
        data (Dict): Dictionary containing book data with keys:
                     isbn, title, author, publication, year, category, copies

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
                          is_valid=True and error_message='' if valid
                          is_valid=False and error_message contains reason if invalid

    Example:
        >>> data = {'isbn': '123', 'title': 'Book', 'author': 'Author', ...}
        >>> is_valid, msg = validate_book_data(data)
    """
    required_fields = ['isbn', 'title', 'author', 'publication', 'year', 'category']
    
    # Check all required fields present
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate ISBN
    if not is_valid_isbn(data['isbn']):
        return False, "Invalid ISBN format"
    
    # Validate year
    try:
        year = int(data['year'])
        if year < 1900 or year > datetime.now().year + 5:
            return False, f"Year {year} is not reasonable"
    except ValueError:
        return False, "Year must be a number"
    
    # Validate copies
    try:
        copies = int(data.get('copies', 1))
        if copies < 1:
            return False, "Copies must be at least 1"
    except ValueError:
        return False, "Copies must be a number"
    
    return True, ""


def get_overdue_books(records: Dict[str, BorrowRecord]) -> List[BorrowRecord]:
    """
    Filter and return all overdue books from borrow records.

    Args:
        records (Dict[str, BorrowRecord]): Dictionary of borrow records

    Returns:
        List[BorrowRecord]: List of records with unreturned books past due date

    Example:
        >>> overdue = get_overdue_books(library.records)
        >>> print(f"Overdue books: {len(overdue)}")
    """
    now = datetime.now()
    overdue = []
    
    for record in records.values():
        # Check if book is not returned AND past due date
        if not record.is_returned and record.due_date < now:
            overdue.append(record)
    
    return overdue


def calculate_total_fines(records: Dict[str, BorrowRecord], fine_strategy) -> float:
    """
    Calculate total fines for all overdue books.

    Args:
        records (Dict[str, BorrowRecord]): Dictionary of borrow records
        fine_strategy: Fine calculation strategy instance

    Returns:
        float: Total fine amount in dollars

    Example:
        >>> total = calculate_total_fines(library.records, strategy)
        >>> print(f"Total fines owed: ${total:.2f}")
    """
    total_fines = 0.0
    now = datetime.now()
    
    for record in records.values():
        if not record.is_returned and record.due_date < now:
            fine = fine_strategy.calculate(record.due_date, now)
            total_fines += fine
    
    return total_fines


def get_borrower_history(records: Dict[str, BorrowRecord], borrower_id: str) -> List[BorrowRecord]:
    """
    Get all borrow records for a specific borrower.

    Args:
        records (Dict[str, BorrowRecord]): Dictionary of all borrow records
        borrower_id (str): Student or Staff ID of the borrower

    Returns:
        List[BorrowRecord]: All records for the specified borrower

    Example:
        >>> history = get_borrower_history(library.records, 'STU001')
        >>> print(f"Borrower has {len(history)} records")
    """
    return [record for record in records.values() if record.borrower_id == borrower_id]


def get_book_popularity(records: Dict[str, BorrowRecord]) -> Dict[str, int]:
    """
    Calculate how many times each book has been borrowed.

    Args:
        records (Dict[str, BorrowRecord]): Dictionary of all borrow records

    Returns:
        Dict[str, int]: Dictionary mapping book_title to borrow count

    Example:
        >>> popularity = get_book_popularity(library.records)
        >>> most_borrowed = max(popularity, key=popularity.get)
    """
    popularity = {}
    
    for record in records.values():
        book_title = record.book_title
        if book_title not in popularity:
            popularity[book_title] = 0
        popularity[book_title] += 1
    
    return popularity
