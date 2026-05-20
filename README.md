# Library Borrowing and Returning Books

A comprehensive library management system that streamlines the process of borrowing and returning books. Built with Python backend, HTML/CSS frontend, this application provides an intuitive platform for both patrons and library administrators.

## 🎯 Features

- **Book Catalog Management** - Browse and search available books in the library collection
- **User Authentication** - Secure login and registration system for patrons
- **Borrowing System** - Easy-to-use interface for borrowing books with due date tracking
- **Return Management** - Streamlined book return process with condition tracking
- **Loan History** - View personal borrowing history and current loans
- **Inventory Management** - Admin panel for managing book inventory and availability
- **Due Date Reminders** - Notifications for upcoming and overdue returns
- **Penalty System** - Track and manage late fees and penalties
- **User Profiles** - Manage personal information and borrowing preferences

## 💻 Tech Stack

- **Backend:** Python
- **Frontend:** HTML 
- **Styling:** CSS 

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- A modern web browser
- SQLite or PostgreSQL (depending on configuration)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pateyma-123/Library-Borrowing-and-Returning-Books.git
   cd Library-Borrowing-and-Returning-Books
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python manage.py migrate
   # or
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   # or for Flask/Django
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and navigate to `http://localhost:5000` (or your configured port)

## 📖 Usage

### For Patrons
1. Register or log in to your account
2. Browse the library catalog by title, author, or category
3. Click "Borrow" on any available book
4. View your active loans and due dates in "My Loans"
5. Return books through the "Return Book" section
6. Check your borrowing history anytime

### For Administrators
1. Log in with admin credentials
2. Access the Admin Dashboard
3. Manage book inventory - add, update, or remove books
4. View all user accounts and their borrowing status
5. Monitor overdue books and manage penalties
6. Generate reports on library usage and statistics

## 📁 Project Structure

```
Library-Borrowing-and-Returning-Books/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── models/               # Data models
│   ├── user.py
│   ├── book.py
│   └── loan.py
├── routes/               # Application routes
│   ├── auth.py
│   ├── books.py
│   └── loans.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── books.html
│   ├── borrow.html
│   └── admin.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── README.md            # This file
```

## 🔐 Security Features

- Password hashing and salting
- SQL injection prevention
- CSRF protection
- Secure session management
- Input validation and sanitization

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows PEP 8 standards and includes appropriate documentation.

## 📝 License

This project is licensed under the MIT License - see the details below:

```
MIT License

Copyright (c) 2026 pateyma-123

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

## 📞 Support

If you encounter any issues or have questions:
- Open an [Issue](https://github.com/pateyma-123/Library-Borrowing-and-Returning-Books/issues)
- Check existing issues for solutions
- Contact the development team through the repository discussions

## 🙏 Acknowledgments

- Thanks to all contributors who have helped improve this project
- Special thanks to the open-source community for the tools and libraries used

---

**Happy reading! 📚**
