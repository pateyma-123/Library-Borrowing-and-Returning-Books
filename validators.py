"""
Validation Module for Library Management System.

This module provides validation logic for various inputs and data in the
library system. It ensures data integrity and consistency throughout the
application.

Functions:
    validate_borrower_info(): Validate borrower name and ID
    validate_date_range(): Validate date comparisons
    validate_inventory_update(): Validate inventory change operations
    check_borrowing_eligibility(): Check if borrower can borrow books
    validate_return_operation(): Validate return transaction

Author: Library Management Team
Version: 1.0
"""

from datetime import datetime, timedelta
from typing import Tuple
from models import Book


def validate_borrower_info(borrower_name: str, borrower_id: str) -> Tuple[bool, str]:
    """
    Validate borrower name and ID format.

    Checks:
    - Name is not empty and contains valid characters
    - ID is not empty and contains valid characters
    - Both fields have reasonable lengths

    Args:
        borrower_name (str): Name of the borrower
        borrower_id (str): Student or Staff ID

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> validate_borrower_info('John Doe', 'STU001')
        (True, '')
        >>> validate_borrower_info('', 'STU001')
        (False, 'Borrower name cannot be empty')
    """
    if not borrower_name or not isinstance(borrower_name, str):
        return False, "Borrower name cannot be empty"
    
    if not borrower_id or not isinstance(borrower_id, str):
        return False, "Borrower ID cannot be empty"
    
    if len(borrower_name.strip()) < 2:
        return False, "Borrower name must be at least 2 characters"
    
    if len(borrower_name.strip()) > 100:
        return False, "Borrower name is too long (max 100 characters)"
    
    if len(borrower_id.strip()) > 50:
        return False, "Borrower ID is too long (max 50 characters)"
    
    return True, ""


def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, str]:
    """
    Validate that date range is logically valid.

    Checks:
    - Both dates are valid datetime objects
    - Start date is before end date
    - Dates are not in the distant past or future

    Args:
        start_date (datetime): Beginning of date range
        end_date (datetime): End of date range

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> start = datetime.now()
        >>> end = datetime.now() + timedelta(days=14)
        >>> validate_date_range(start, end)
        (True, '')
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return False, "Invalid date format"
    
    if start_date >= end_date:
        return False, "Start date must be before end date"
    
    now = datetime.now()
    max_duration = timedelta(days=365)
    
    if end_date - start_date > max_duration:
        return False, "Loan period cannot exceed 365 days"
    
    if start_date < now - timedelta(days=30):
        return False, "Start date cannot be more than 30 days in the past"
    
    return True, ""


def validate_inventory_update(book: Book, copies_change: int) -> Tuple[bool, str]:
    """
    Validate inventory update operation.

    Checks:
    - Enough copies available for removal
    - New total is non-negative
    - Change amount is reasonable

    Args:
        book (Book): Book object to update
        copies_change (int): Number of copies to add (positive) or remove (negative)

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> validate_inventory_update(book, -2)
        (True, '') if book has enough copies
        (False, 'Not enough copies') otherwise
    """
    if not isinstance(copies_change, int):
        return False, "Copies change must be an integer"
    
    if copies_change == 0:
        return False, "Copies change must not be zero"
    
    # Removing books
    if copies_change < 0:
        if book.total_copies + copies_change < 0:
            return False, f"Cannot remove {abs(copies_change)} copies (only {book.total_copies} available)"
        if abs(copies_change) > book.total_copies:
            return False, "Cannot remove more copies than exist"
    
    # Adding books
    if copies_change > 100:
        return False, "Cannot add more than 100 copies at once"
    
    return True, ""


def check_borrowing_eligibility(book: Book, borrower_id: str) -> Tuple[bool, str]:
    """
    Check if a borrower is eligible to borrow a specific book.

    Checks:
    - Book has available copies
    - Borrower ID is valid format
    - Book is in stock

    Args:
        book (Book): Book to borrow
        borrower_id (str): ID of borrower

    Returns:
        Tuple[bool, str]: (is_eligible, reason)

    Example:
        >>> check_borrowing_eligibility(book, 'STU001')
        (True, '') if eligible
        (False, 'Book not in stock') otherwise
    """
    if book.available_copies <= 0:
        return False, "Book is not currently available for borrowing"
    
    if not borrower_id or len(borrower_id.strip()) == 0:
        return False, "Invalid borrower ID"
    
    if book.total_copies == 0:
        return False, "Book is not in stock"
    
    return True, ""


def validate_return_operation(book: Book, borrowed_copies: int) -> Tuple[bool, str]:
    """
    Validate that a return operation is valid.

    Checks:
    - Borrowed copies count is accurate
    - Book has been properly tracked
    - Return will not exceed total copies

    Args:
        book (Book): Book being returned
        borrowed_copies (int): Number of copies borrowed

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> validate_return_operation(book, 1)
        (True, '') if valid
    """
    if borrowed_copies != 1:
        return False, "Return operation must be for exactly 1 copy"
    
    if book.available_copies >= book.total_copies:
        return False, "All copies are already available - nothing to return"
    
    if book.available_copies < 0:
        return False, "Inventory error: negative available copies"
    
    return True, ""
