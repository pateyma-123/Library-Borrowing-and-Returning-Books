"""
Data Analytics Module for Library Management System.

This module provides analytics and reporting functions to generate insights
from library data. It calculates statistics, generates reports, and provides
data analysis tools for understanding library usage patterns.

Classes:
    LibraryAnalytics: Main analytics engine for library data

Functions:
    analyze_borrowing_patterns(): Analyze when books are borrowed
    get_busiest_period(): Find peak borrowing times
    generate_annual_report(): Create comprehensive annual statistics

Author: Library Management Team
Version: 1.0
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter
from models import Book, BorrowRecord


class LibraryAnalytics:
    """
    Analytics engine for library management system.

    Provides methods to analyze borrowing patterns, generate reports,
    and extract insights from library data.

    Attributes:
        books (Dict[str, Book]): Reference to library's book inventory
        records (Dict[str, BorrowRecord]): Reference to borrow records
    """

    def __init__(self, books: Dict[str, Book], records: Dict[str, BorrowRecord]):
        """
        Initialize analytics engine.

        Args:
            books (Dict[str, Book]): Dictionary of Book objects
            records (Dict[str, BorrowRecord]): Dictionary of BorrowRecord objects
        """
        self.books = books
        self.records = records

    def get_total_books(self) -> int:
        """
        Get total count of unique book titles in inventory.

        Returns:
            int: Number of unique books
        """
        return len(self.books)

    def get_total_copies(self) -> int:
        """
        Get total count of all book copies (including all copies of same title).

        Returns:
            int: Total copies across all books
        """
        return sum(book.total_copies for book in self.books.values())

    def get_available_copies(self) -> int:
        """
        Get count of books currently available for borrowing.

        Returns:
            int: Number of available copies
        """
        return sum(book.available_copies for book in self.books.values())

    def get_borrowed_copies(self) -> int:
        """
        Get count of books currently borrowed (checked out).

        Returns:
            int: Number of copies currently borrowed
        """
        return self.get_total_copies() - self.get_available_copies()

    def get_category_distribution(self) -> Dict[str, int]:
        """
        Get distribution of books by category.

        Returns:
            Dict[str, int]: Dictionary mapping category names to book counts

        Example:
            {'Programming': 15, 'Fiction': 8, 'History': 5}
        """
        categories = {}
        for book in self.books.values():
            if book.category not in categories:
                categories[book.category] = 0
            categories[book.category] += 1
        return categories

    def get_author_statistics(self) -> Dict[str, int]:
        """
        Get count of books by each author.

        Returns:
            Dict[str, int]: Dictionary mapping author names to book counts
        """
        authors = {}
        for book in self.books.values():
            if book.author not in authors:
                authors[book.author] = 0
            authors[book.author] += 1
        return authors

    def get_active_borrows_count(self) -> int:
        """
        Get count of currently active (not returned) borrow records.

        Returns:
            int: Number of active borrows
        """
        return sum(1 for record in self.records.values() if not record.is_returned)

    def get_return_history_count(self) -> int:
        """
        Get count of completed (returned) borrow records.

        Returns:
            int: Number of returned books
        """
        return sum(1 for record in self.records.values() if record.is_returned)

    def get_overdue_count(self) -> int:
        """
        Get count of overdue books (not returned and past due date).

        Returns:
            int: Number of overdue books
        """
        now = datetime.now()
        return sum(1 for record in self.records.values() 
                   if not record.is_returned and record.due_date < now)

    def get_top_borrowed_books(self, limit: int = 5) -> List[Tuple[str, int]]:
        """
        Get the most frequently borrowed books.

        Args:
            limit (int): Maximum number of books to return (default: 5)

        Returns:
            List[Tuple[str, int]]: List of (book_title, borrow_count) tuples
                                   sorted by frequency in descending order

        Example:
            [('Python 101', 5), ('Web Design', 4), ('Data Science', 3)]
        """
        book_borrows = Counter(record.book_title for record in self.records.values())
        return book_borrows.most_common(limit)

    def get_borrower_statistics(self) -> Dict[str, int]:
        """
        Get count of books borrowed by each borrower.

        Returns:
            Dict[str, int]: Dictionary mapping borrower names to borrow counts
        """
        borrowers = {}
        for record in self.records.values():
            if record.borrower_name not in borrowers:
                borrowers[record.borrower_name] = 0
            borrowers[record.borrower_name] += 1
        return borrowers

    def get_borrowing_by_month(self) -> Dict[str, int]:
        """
        Get count of borrows by month.

        Returns:
            Dict[str, int]: Dictionary mapping months (YYYY-MM) to borrow counts
        """
        monthly = {}
        for record in self.records.values():
            month_key = record.borrow_date.strftime('%Y-%m')
            if month_key not in monthly:
                monthly[month_key] = 0
            monthly[month_key] += 1
        return monthly

    def get_average_borrow_duration(self) -> float:
        """
        Calculate average number of days books are borrowed.

        Returns:
            float: Average duration in days (only counts returned books)
        """
        returned_records = [r for r in self.records.values() if r.is_returned and r.return_date]
        
        if not returned_records:
            return 0.0
        
        total_days = sum(
            (record.return_date - record.borrow_date).days 
            for record in returned_records
        )
        
        return total_days / len(returned_records)

    def generate_summary_report(self) -> Dict:
        """
        Generate comprehensive summary report of library statistics.

        Returns:
            Dict: Dictionary containing all key statistics

        Example:
            {
                'total_books': 50,
                'total_copies': 120,
                'available': 85,
                'borrowed': 35,
                'overdue': 2,
                'active_borrows': 35,
                'completed_returns': 150
            }
        """
        return {
            'total_books': self.get_total_books(),
            'total_copies': self.get_total_copies(),
            'available': self.get_available_copies(),
            'borrowed': self.get_borrowed_copies(),
            'overdue': self.get_overdue_count(),
            'active_borrows': self.get_active_borrows_count(),
            'completed_returns': self.get_return_history_count(),
            'avg_borrow_duration': round(self.get_average_borrow_duration(), 2),
            'categories': self.get_category_distribution(),
            'top_books': self.get_top_borrowed_books(5)
        }
