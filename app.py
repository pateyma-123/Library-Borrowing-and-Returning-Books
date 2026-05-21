"""
Flask Application for Library Management System.

This module serves as the entry point for the web application.
It defines routes for viewing inventory, adding/removing books,
borrowing books, and processing returns.
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
    Render the main page.

    Displays book inventory, active borrows, and return history.
    Handles selection of books for borrowing and displays flash messages.

    Returns:
        str: Rendered HTML content for index.html.
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

    Extracts book details from the form and calls the library manager.
    Redirects back to index with a success or error message.

    Returns:
        redirect: A Flask redirect response to the index page.
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
        isbn (str): The ISBN of the book to remove.

    Returns:
        redirect: A Flask redirect response to the index page.
    """
    success, msg = library.remove_book(isbn)
    return redirect(url_for('index', msg=msg if success else None, err=msg if not success else None))


@app.route('/search')
def search():
    """
    Handle search requests.

    Determines the search field (title or author) and applies the
    corresponding search strategy. Renders index.html with filtered results.

    Returns:
        str: Rendered HTML content for index.html with search results.
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

    Returns:
        redirect: A Flask redirect response to the index page.
    """
    isbn = request.form['isbn']
    name = request.form['borrower_name']
    bid = request.form['borrower_id']

    # Calculate days from selected date
    due_date_str 