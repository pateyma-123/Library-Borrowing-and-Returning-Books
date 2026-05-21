"""
Logging Module for Library Management System.

This module provides comprehensive logging functionality for tracking all
events and operations in the library system. It helps with debugging,
auditing, and monitoring system activity.

Functions:
    setup_logging(): Initialize logging system
    log_book_added(): Log book addition
    log_book_removed(): Log book removal
    log_borrow_operation(): Log borrowing transaction
    log_return_operation(): Log book return
    log_fine_calculated(): Log fine calculation
    log_search_operation(): Log search activity

Classes:
    EventLogger: Main logging manager

Author: Library Management Team
Version: 1.0
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum


class EventType(Enum):
    """
    Enumeration of all event types that can be logged.

    Event Types:
        BOOK_ADDED: New book added to inventory
        BOOK_REMOVED: Book removed from inventory
        BOOK_UPDATED: Book details updated
        BORROW_INITIATED: Borrowing transaction started
        BORROW_COMPLETED: Borrowing transaction completed
        RETURN_INITIATED: Return process started
        RETURN_COMPLETED: Return completed
        FINE_CALCULATED: Fine amount calculated
        SEARCH_EXECUTED: Search query executed
        ERROR_OCCURRED: Error or exception occurred
        ACCESS_ATTEMPT: System access attempt
    """
    BOOK_ADDED = "BOOK_ADDED"
    BOOK_REMOVED = "BOOK_REMOVED"
    BOOK_UPDATED = "BOOK_UPDATED"
    BORROW_INITIATED = "BORROW_INITIATED"
    BORROW_COMPLETED = "BORROW_COMPLETED"
    RETURN_INITIATED = "RETURN_INITIATED"
    RETURN_COMPLETED = "RETURN_COMPLETED"
    FINE_CALCULATED = "FINE_CALCULATED"
    SEARCH_EXECUTED = "SEARCH_EXECUTED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    ACCESS_ATTEMPT = "ACCESS_ATTEMPT"


class EventLogger:
    """
    Centralized event logging system for library operations.

    Provides methods to log various library events with timestamps,
    severity levels, and detailed information.

    Attributes:
        logger (logging.Logger): Python logger instance
        events (List[Dict]): In-memory event log
    """

    def __init__(self, name: str = "LibrarySystem"):
        """
        Initialize the event logger.

        Args:
            name (str): Logger name (default: "LibrarySystem")
        """
        self.logger = logging.getLogger(name)
        self.events = []

    def setup(self, log_file: Optional[str] = None, level=logging.INFO) -> None:
        """
        Setup logging configuration.

        Args:
            log_file (str): Path to log file (optional)
            level: Logging level (default: logging.INFO)
        """
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.setLevel(level)

    def log_event(self, event_type: EventType, details: Dict[str, Any], 
                  level: str = "INFO") -> None:
        """
        Log a library system event.

        Args:
            event_type (EventType): Type of event to log
            details (Dict): Event details and context
            level (str): Log level ('INFO', 'WARNING', 'ERROR', 'DEBUG')
        """
        event_record = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type.value,
            'level': level,
            'details': details
        }
        self.events.append(event_record)

        message = f"{event_type.value}: {details}"
        getattr(self.logger, level.lower())(message)

    def log_book_added(self, isbn: str, title: str, author: str, copies: int) -> None:
        """
        Log book addition to inventory.

        Args:
            isbn (str): Book ISBN
            title (str): Book title
            author (str): Author name
            copies (int): Number of copies added
        """
        self.log_event(EventType.BOOK_ADDED, {
            'isbn': isbn,
            'title': title,
            'author': author,
            'copies': copies
        })

    def log_book_removed(self, isbn: str, title: str, reason: str = None) -> None:
        """
        Log book removal from inventory.

        Args:
            isbn (str): Book ISBN
            title (str): Book title
            reason (str): Reason for removal (optional)
        """
        self.log_event(EventType.BOOK_REMOVED, {
            'isbn': isbn,
            'title': title,
            'reason': reason or 'Manual removal'
        })

    def log_borrow_operation(self, isbn: str, title: str, borrower: str, 
                            borrower_id: str, due_date: str) -> None:
        """
        Log borrowing transaction.

        Args:
            isbn (str): Book ISBN
            title (str): Book title
            borrower (str): Borrower name
            borrower_id (str): Borrower ID
            due_date (str): Due date string
        """
        self.log_event(EventType.BORROW_COMPLETED, {
            'isbn': isbn,
            'title': title,
            'borrower': borrower,
            'borrower_id': borrower_id,
            'due_date': due_date
        })

    def log_return_operation(self, record_id: str, title: str, 
                            borrower: str, fine: float) -> None:
        """
        Log book return transaction.

        Args:
            record_id (str): Borrow record ID
            title (str): Book title
            borrower (str): Borrower name
            fine (float): Fine amount (if any)
        """
        self.log_event(EventType.RETURN_COMPLETED, {
            'record_id': record_id,
            'title': title,
            'borrower': borrower,
            'fine': fine
        })

    def log_fine_calculated(self, record_id: str, title: str, 
                           overdue_days: int, fine_amount: float) -> None:
        """
        Log fine calculation.

        Args:
            record_id (str): Borrow record ID
            title (str): Book title
            overdue_days (int): Number of days overdue
            fine_amount (float): Calculated fine
        """
        self.log_event(EventType.FINE_CALCULATED, {
            'record_id': record_id,
            'title': title,
            'overdue_days': overdue_days,
            'fine_amount': fine_amount
        })

    def log_search_operation(self, query: str, field: str, result_count: int) -> None:
        """
        Log search operation.

        Args:
            query (str): Search query
            field (str): Field searched (title, author, etc.)
            result_count (int): Number of results found
        """
        self.log_event(EventType.SEARCH_EXECUTED, {
            'query': query,
            'field': field,
            'results_found': result_count
        })

    def log_error(self, error_type: str, message: str, context: Dict = None) -> None:
        """
        Log an error or exception.

        Args:
            error_type (str): Type of error
            message (str): Error message
            context (Dict): Additional error context
        """
        error_details = {
            'error_type': error_type,
            'message': message,
            'context': context or {}
        }
        self.log_event(EventType.ERROR_OCCURRED, error_details, level="ERROR")

    def get_event_count(self, event_type: Optional[EventType] = None) -> int:
        """
        Get count of logged events.

        Args:
            event_type (EventType): Filter by event type (optional)

        Returns:
            int: Number of events
        """
        if event_type is None:
            return len(self.events)
        return sum(1 for e in self.events if e['event_type'] == event_type.value)

    def get_events_by_type(self, event_type: EventType) -> list:
        """
        Get all events of a specific type.

        Args:
            event_type (EventType): Event type to filter

        Returns:
            list: List of matching events
        """
        return [e for e in self.events if e['event_type'] == event_type.value]

    def get_recent_events(self, limit: int = 10) -> list:
        """
        Get most recent events.

        Args:
            limit (int): Number of recent events to return

        Returns:
            list: List of recent events
        """
        return self.events[-limit:]

    def clear_events(self) -> None:
        """
        Clear all logged events (in-memory only).
        """
        self.events = []
        self.logger.info("Event log cleared")

    def get_event_summary(self) -> Dict[str, int]:
        """
        Get summary of event counts by type.

        Returns:
            Dict: Event type to count mapping
        """
        summary = {}
        for event_type in EventType:
            count = self.get_event_count(event_type)
            if count > 0:
                summary[event_type.value] = count
        return summary


# Global logger instance
_global_logger = EventLogger()


def get_logger() -> EventLogger:
    """
    Get the global event logger instance.

    Returns:
        EventLogger: Global logger instance
    """
    return _global_logger
