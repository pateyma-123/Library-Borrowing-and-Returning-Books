"""
Flask Application for Library Management System.

This module serves as the entry point for the web application.
It defines routes for viewing inventory, adding/removing books,
borrowing books, and processing returns.

Modules:
    - flask: Web framework for routing and template rendering
    - library_system: Core library management logic
    - strategies: Search and fine calculation strategies
    - models: Data models for Book and BorrowRecord

Functions:
    index(): Display main dashboard with inventory and active borrows
    add_book(): POST handler to add new book to inventory
    remove_book(): Remove book by ISBN
    search(): Search books by title or author
    borrow_book(): Process book borrowing transaction
    return_book(): Process book return and calculate fines

Author: Library Management Team
Version: 1.0
"""

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from library_system import LibraryManager
from strategies import AuthorSearchStrategy, TitleSearchStrategy

app = Flask(__name__)

# Initialize Library System
library = LibraryManager("Library Borrowing & Returning Books")

# Pre-populate sample data ONLY if library is empty (First Run)
if len(library.get_all_books()) == 0:
    print("No data found. Populating sample data...")
    library.add_book("978-0134685991", "The Python Programming Language", "Guido van Rossum", "Pearson", 2020,
                     "Programming", 5)
    library.add_book("978-1593279288", "Python Crash Course", "Eric Matthes", "No Starch Press", 2019, "Programming", 3)
    library.add_book("978-1491912058", "Fluent Python", "Luciano Ramalho", "O'Reilly Media", 2022, "Programming", 2)


@app.route('/')
def index():
    """
    Render the main dashboard page.

    Displays:
        - Book inventory with search functionality
        - Active borrows by patrons
        - Recent return history
        - Borrowing form for selected books

    Query Parameters:
        - borrow_isbn (str): ISBN of book to borrow
        - msg (str): Success message to display
        - err (str): Error message to display

    Returns:
        Rendered index.html template with library data and statistics
    """
    stats = library.get_stats()
    active_borrows = library.get_active_borrows()
    history = library.get_return_history()[-5:]

    selected_isbn = request.args.get('borrow_isbn')
    selected_book = library.books.get(selected_isbn) if selected_isbn else None

    # Get today's date for the date picker min attribute
    today_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('index.html',
                           library=library,
                           stats=stats,
                           books=library.get_all_books(),
                           active_borrows=active_borrows,
                           history=history,
                           selected_book=selected_book,
                           today_date=today_date,
                           message=request.args.get('msg'),
                           error=request.args.get('err'))


@app.route('/inventory/add', methods=['POST'])
def add_book():
    """
    Handle POST request to add a new book to the inventory.

    Extracts book details from form submission and calls the library manager
    to persist data. Validates all required fields are provided.

    Form Parameters:
        - isbn (str): Unique book identifier
        - title (str): Book title
        - author (str): Author name
        - publication (str): Publisher name
        - year (int): Publication year
        - category (str): Book category/genre
        - copies (int): Number of copies to add (default: 1)

    Returns:
        Redirect to index with success or error message
    """
    success, msg = library.add_book(
        request.form['isbn'],
        request.form['title'],
        request.form['author'],
        request.form['publication'],
        int(request.form['year']),
        request.form['category'],
        int(request.form.get('copies', 1))
    )
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/inventory/remove/<isbn>')
def remove_book(isbn):
    """
    Handle request to remove a book from inventory by ISBN.

    Args:
        isbn (str): ISBN of the book to remove

    Returns:
        Redirect to index with status message
    """
    success, msg = library.remove_book(isbn)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/search')
def search():
    """
    Handle search requests for books.

    Determines the search field (title or author) from query parameters
    and applies the corresponding search strategy to filter results.

    Query Parameters:
        - q (str): Search query
        - field (str): Search field - 'title' or 'author' (default: 'title')

    Returns:
        Rendered index.html template with filtered search results
    """
    query = request.args.get('q', '')
    field = request.args.get('field', 'title')

    if field == 'author':
        library.set_search_strategy(AuthorSearchStrategy())
    else:
        library.set_search_strategy(TitleSearchStrategy())

    results = library.search_books(query)

    return render_template('index.html',
                           library=library,
                           stats=library.get_stats(),
                           books=results,
                           active_borrows=library.get_active_borrows(),
                           history=library.get_return_history(),
                           selected_book=None,
                           today_date=datetime.now().strftime('%Y-%m-%d'),
                           search_query=query)


@app.route('/borrow', methods=['POST'])
def borrow_book():
    """
    Process a book borrowing transaction.

    Validates the due date selected by the user, calculates the loan duration,
    and registers the borrow record in the system.

    Form Parameters:
        - isbn (str): ISBN of book to borrow
        - borrower_name (str): Name of the borrower
        - borrower_id (str): Student or Staff ID
        - due_date (str): Return date in YYYY-MM-DD format

    Returns:
        Redirect to index with success/error message
    """
    isbn = request.form['isbn']
    name = request.form['borrower_name']
    bid = request.form['borrower_id']

    # Calculate days from selected date
    due_date_str = request.form.get('due_date')
    days = 14  # Default fallback

    if due_date_str:
        try:
            due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d')
            now = datetime.now()
            # Calculate difference in days
            delta = due_date_obj - now
            days = delta.days
            if days < 1:
                days = 1  # Minimum 1 day
        except ValueError:
            days = 14  # Fallback if date parsing fails

    success, msg = library.borrow_book(isbn, name, bid, days)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/return/<record_id>')
def return_book(record_id):
    """
    Process a book return transaction and calculate any fines.

    Marks the book as returned, restores inventory, and calculates
    late fees if the return exceeds the due date.

    Args:
        record_id (str): Unique identifier for the borrow record

    Returns:
        Redirect to index with return confirmation and fine details
    """
    success, msg, fine = library.return_book(record_id)
    fine_info = f" Fine: ${fine:.2f}" if fine > 0 else ""
    full_msg = msg + fine_info
    return redirect(url_for('index', msg=full_msg if success else None, err=full_msg if not success else None))


if __name__ == '__main__':
    app.run(debug=True)
