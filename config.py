"""
Configuration Module for Library Management System.

This module manages application configuration, settings, and constants used
throughout the library system. It provides centralized configuration management
for easy updates and consistency.

Constants:
    DEFAULT_LOAN_DAYS: Default number of days for book loans
    MAX_BOOK_COPIES: Maximum copies per book addition
    FINE_RATE: Daily fine rate for overdue books
    CSV_ENCODING: Encoding for CSV file operations

Configuration Classes:
    LibraryConfig: Main configuration holder
    ValidationConfig: Validation rules and constraints
    FineConfig: Fine calculation parameters

Author: Library Management Team
Version: 1.0
"""

from typing import Dict, List
from dataclasses import dataclass


# ===================== Constants =====================

DEFAULT_LOAN_DAYS = 14
MIN_LOAN_DAYS = 1
MAX_LOAN_DAYS = 365

DEFAULT_FINE_RATE = 0.50  # $0.50 per day
MAX_FINE_PER_DAY = 5.00

MAX_BOOK_COPIES = 100
MAX_BOOKS_PER_BORROWER = 5

CSV_ENCODING = 'utf-8'
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

VALID_CATEGORIES = [
    'Programming',
    'Fiction',
    'Non-Fiction',
    'History',
    'Science',
    'Mathematics',
    'Art',
    'Business',
    'Technology',
    'Education',
    'Biography',
    'Mystery',
    'Other'
]

ISBN_LENGTHS = [10, 13]  # Valid ISBN lengths
MIN_YEAR = 1900
MAX_YEAR_OFFSET = 5  # Books up to 5 years in the future

# Borrower constraints
MIN_BORROWER_NAME_LENGTH = 2
MAX_BORROWER_NAME_LENGTH = 100
MAX_BORROWER_ID_LENGTH = 50


# ===================== Configuration Classes =====================

@dataclass
class ValidationConfig:
    """
    Validation rules and constraints for the library system.

    Attributes:
        min_borrower_name_len (int): Minimum borrower name length
        max_borrower_name_len (int): Maximum borrower name length
        max_borrower_id_len (int): Maximum borrower ID length
        min_isbn_length (int): Minimum ISBN length
        max_isbn_length (int): Maximum ISBN length
        valid_categories (List[str]): Allowed book categories
        min_book_year (int): Earliest valid publication year
        max_book_year (int): Latest valid publication year
    """
    min_borrower_name_len: int = MIN_BORROWER_NAME_LENGTH
    max_borrower_name_len: int = MAX_BORROWER_NAME_LENGTH
    max_borrower_id_len: int = MAX_BORROWER_ID_LENGTH
    min_isbn_length: int = 10
    max_isbn_length: int = 13
    valid_categories: List[str] = None
    min_book_year: int = MIN_YEAR
    max_book_year: int = None

    def __post_init__(self):
        """Initialize default values."""
        if self.valid_categories is None:
            self.valid_categories = VALID_CATEGORIES
        if self.max_book_year is None:
            from datetime import datetime
            self.max_book_year = datetime.now().year + MAX_YEAR_OFFSET


@dataclass
class FineConfig:
    """
    Fine calculation configuration.

    Attributes:
        daily_rate (float): Fine amount per day overdue
        max_daily_fine (float): Maximum fine per single day
        grace_days (int): Days before fines start accruing
        fine_rounding (str): How to round calculated fines ('up', 'down', 'nearest')
    """
    daily_rate: float = DEFAULT_FINE_RATE
    max_daily_fine: float = MAX_FINE_PER_DAY
    grace_days: int = 0
    fine_rounding: str = 'nearest'  # 'up', 'down', 'nearest'

    def validate(self) -> bool:
        """
        Validate fine configuration.

        Returns:
            bool: True if configuration is valid
        """
        if self.daily_rate < 0 or self.daily_rate > self.max_daily_fine:
            return False
        if self.grace_days < 0:
            return False
        if self.fine_rounding not in ['up', 'down', 'nearest']:
            return False
        return True


@dataclass
class LibraryConfig:
    """
    Main configuration holder for the entire library system.

    Provides centralized access to all configuration settings and allows
    for easy updates and modifications.

    Attributes:
        library_name (str): Name of the library
        default_loan_days (int): Default loan period in days
        max_loans_per_borrower (int): Maximum concurrent borrows per person
        max_copies_per_addition (int): Maximum copies to add at once
        csv_encoding (str): Encoding for file operations
        validation_config (ValidationConfig): Validation settings
        fine_config (FineConfig): Fine calculation settings
    """
    library_name: str = "Central Library"
    default_loan_days: int = DEFAULT_LOAN_DAYS
    max_loans_per_borrower: int = MAX_BOOKS_PER_BORROWER
    max_copies_per_addition: int = MAX_BOOK_COPIES
    csv_encoding: str = CSV_ENCODING
    validation_config: ValidationConfig = None
    fine_config: FineConfig = None

    def __post_init__(self):
        """Initialize default configuration objects."""
        if self.validation_config is None:
            self.validation_config = ValidationConfig()
        if self.fine_config is None:
            self.fine_config = FineConfig()

    def validate(self) -> bool:
        """
        Validate entire configuration.

        Returns:
            bool: True if all settings are valid
        """
        if self.default_loan_days < MIN_LOAN_DAYS or self.default_loan_days > MAX_LOAN_DAYS:
            return False
        if self.max_loans_per_borrower < 1:
            return False
        if self.max_copies_per_addition < 1 or self.max_copies_per_addition > MAX_BOOK_COPIES:
            return False
        if not self.fine_config.validate():
            return False
        return True

    def get_summary(self) -> Dict:
        """
        Get configuration summary as dictionary.

        Returns:
            Dict: Configuration settings summary
        """
        return {
            'library_name': self.library_name,
            'default_loan_days': self.default_loan_days,
            'max_loans_per_borrower': self.max_loans_per_borrower,
            'max_copies_per_addition': self.max_copies_per_addition,
            'daily_fine_rate': self.fine_config.daily_rate,
            'max_daily_fine': self.fine_config.max_daily_fine
        }


# ===================== Default Configuration Instance =====================

DEFAULT_CONFIG = LibraryConfig(
    library_name="Library Borrowing & Returning Books",
    default_loan_days=DEFAULT_LOAN_DAYS,
    max_loans_per_borrower=MAX_BOOKS_PER_BORROWER,
    max_copies_per_addition=MAX_BOOK_COPIES
)


def get_config() -> LibraryConfig:
    """
    Get the default library configuration.

    Returns:
        LibraryConfig: Global configuration instance
    """
    return DEFAULT_CONFIG


def update_config(**kwargs) -> None:
    """
    Update configuration settings.

    Args:
        **kwargs: Configuration fields to update

    Example:
        update_config(default_loan_days=21, library_name="My Library")
    """
    for key, value in kwargs.items():
        if hasattr(DEFAULT_CONFIG, key):
            setattr(DEFAULT_CONFIG, key, value)
