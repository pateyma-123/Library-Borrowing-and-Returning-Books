# app.py
"""
Flask Application for Library Management System.

This module serves as the main entry point for the Library Management web application.
It initializes the Flask app, configures the library system, and defines URL routes
for handling user interactions such as viewing inventory, borrowing books, and
processing returns.

The application uses the `LibraryManager` class for backend logic and follows the
Strategy Pattern for flexible search and fine calculation behaviors.

Dependencies:
    - Flask: For web framework functionality.
    - datetime: For handling date and time operations.
    - library_system: Custom module containing core library logic.
    - strategies: Custom module containing search algorithms.
"""

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from library_system import LibraryManager
from strategies import AuthorSearchStrategy, TitleSearchStrategy

# Initialize the Flask application instance
app = Flask(__name__)

# Initialize the core Library System with a specific name
# This object handles all data persistence and business logic
library = LibraryManager("Library Borrowing & Returning Books")

# Pre-populate sample data ONLY if the library is empty (First Run Logic)
# This ensures that new users have data to interact with immediately upon setup.
if len(library.get_all_books()) == 0:
    print("Status: No existing data found. Populating sample data...")
    library.add_book(
        isbn="978-0134685991",
        title="The Python Programming Language",
        author="Guido van Rossum",
        publication="Pearson",
        year=2020,
        category="Programming",
        copies=5
    )
    library.add_book(
        isbn="978-1593279288",
        title="Python Crash Course",
        author="Eric Matthes",
        publication="No Starch Press",
        year=2019,
        category="Programming",
        copies=3
    )
    library.add_book(
        isbn="978-1491912058",
        title="Fluent Python",
        author="Luciano Ramalho",
        publication="O'Reilly Media",
        year=2022,
        category="Programming",
        copies=2
    )
    print("Status: Sample data loaded successfully.")


@app.route('/')
def index():
    """
    Render the main landing page of the application.

    This view function aggregates data from the library system, including
    statistics, current inventory, active borrows, and recent history.
    It also handles logic for pre-selecting a book when the user clicks 'Borrow'.

    Query Parameters:
        borrow_isbn (str): Optional. The ISBN of a book to pre-select for borrowing.
        msg (str): Optional. A success message to display to the user.
        err (str): Optional. An error message to display to the user.

    Returns:
        flask.Response: Renders the 'index.html' template with the context data.
    """
    # Retrieve library statistics for dashboard display (if any)
    stats = library.get_stats()
    
    # Retrieve lists of books and records to display
    active_borrows = library.get_active_borrows()
    history = library.get_return_history()[-5:]  # Limit history to the last 5 records

    # Check if a specific book is selected for borrowing via URL parameter
    selected_isbn = request.args.get('borrow_isbn')
    selected_book = library.books.get(selected_isbn) if selected_isbn else None

    # Get the current date to set the minimum attribute for the date picker
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Render the template with all necessary data
    return render_template(
        'index.html',
        library=library,
        stats=stats,
        books=library.get_all_books(),
        active_borrows=active_borrows,
        history=history,
        selected_book=selected_book,
        today_date=today_date,
        message=request.args.get('msg'),
        error=request.args.get('err')
    )


@app.route('/inventory/add', methods=['POST'])
def add_book():
    """
    Handle the addition of a new book to the library inventory.

    This route accepts POST data from the 'Add Book' form. It validates the
    input types (converting strings to integers where necessary) and delegates
    the creation logic to the LibraryManager.

    Form Data:
        isbn (str): The International Standard Book Number.
        title (str): The title of the book.
        author (str): The author of the book.
        publication (str): The publication house.
        year (str): The year of publication (converted to int).
        category (str): The genre or category.
        copies (str): Number of copies to add (converted to int, defaults to 1).

    Returns:
        flask.Response: Redirects to the index page with a success or error message.
    """
    # Extract data from the form request object
    success, msg = library.add_book(
        isbn=request.form['isbn'],
        title=request.form['title'],
        author=request.form['author'],
        publication=request.form['publication'],
        year=int(request.form['year']),
        category=request.form['category'],
        copies=int(request.form.get('copies', 1))
    )
    
    # Redirect with appropriate status messages in the URL query string
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/inventory/remove/<isbn>')
def remove_book(isbn):
    """
    Handle the removal of a book from the inventory.

    This route is triggered by a delete link in the inventory table. It attempts
    to remove the book identified by the provided ISBN.

    Args:
        isbn (str): The ISBN of the book to remove.

    Returns:
        flask.Response: Redirects to the index page with a status message.
    """
    success, msg = library.remove_book(isbn)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/search')
def search():
    """
    Handle search queries for the book inventory.

    This function reads the query string to determine what to search for
    and which field to search against (Title or Author). It dynamically
    sets the search strategy on the LibraryManager before executing the search.

    Query Parameters:
        q (str): The search string entered by the user.
        field (str): The field to search within ('title' or 'author').

    Returns:
        flask.Response: Renders 'index.html' with the filtered list of books.
    """
    query = request.args.get('q', '')
    field = request.args.get('field', 'title')

    # Strategy Pattern Implementation:
    # Select the concrete strategy based on user input
    if field == 'author':
        library.set_search_strategy(AuthorSearchStrategy())
    else:
        library.set_search_strategy(TitleSearchStrategy())

    # Execute the search using the selected strategy
    results = library.search_books(query)

    # Render the page with the filtered results
    return render_template(
        'index.html',
        library=library,
        stats=library.get_stats(),
        books=results,
        active_borrows=library.get_active_borrows(),
        history=library.get_return_history(),
        selected_book=None,
        today_date=datetime.now().strftime('%Y-%m-%d'),
        search_query=query
    )


@app.route('/borrow', methods=['POST'])
def borrow_book():
    """
    Process a book borrowing transaction.

    This route handles the submission of the borrowing form. It calculates
    the duration of the loan based on the due date selected by the user
    and registers the transaction in the system.

    Form Data:
        isbn (str): The ISBN of the book being borrowed.
        borrower_name (str): Name of the person borrowing the book.
        borrower_id (str): ID of the person borrowing the book.
        due_date (str): The intended return date (YYYY-MM-DD format).

    Returns:
        flask.Response: Redirects to index with a success or error message.
    """
    isbn = request.form['isbn']
    name = request.form['borrower_name']
    bid = request.form['borrower_id']

    # Logic to calculate the number of days for the loan
    due_date_str = request.form.get('due_date')
    days = 14  # Default fallback duration

    if due_date_str:
        try:
            due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d')
            now = datetime.now()
            # Calculate the difference in days between now and the due date
            delta = due_date_obj - now
            days = delta.days
            if days < 1:
                days = 1  # Enforce a minimum loan period of 1 day
        except ValueError:
            # If date parsing fails, use the default
            pass

    # Delegate the borrowing logic to the library manager
    success, msg = library.borrow_book(isbn, name, bid, days)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/return/<record_id>')
def return_book(record_id):
    """
    Process the return of a borrowed book.

    This route is accessed via the 'Return' button in the sidebar. It marks
    the borrow record as returned and makes the book available again.

    Args:
        record_id (str): The unique ID of the borrow record to close.

    Returns:
        flask.Response: Redirects to index with a status message.
    """
    success, msg, fine = library.return_book(record_id)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


if __name__ == '__main__':
    print("Server starting...")
    print("Access the application at: http://127.0.0.1:5000")
    app.run(debug=True)
