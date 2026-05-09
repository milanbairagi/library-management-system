# Library Management System

A Django-based library management system for tracking book inventory, managing member registrations, processing book loans, and automating fine calculations. Designed for small to medium-sized libraries to streamline day-to-day operations and member interactions.

## Features

- **Book Catalog Management** — Maintain a comprehensive catalog of books with ISBN, title, author, publisher, and subject classification. Track physical copies with unique barcodes and rack locations.
- **Dual User Roles** — Support for Member and Librarian accounts with role-based access control. Members borrow and return books; Librarians manage inventory and process transactions.
- **Loan Tracking** — Issue and track book loans with automatic due date calculation (14-day loan period). Complete loan history for auditing and member accountability.
- **Automated Fine Management** — Automatically calculate fines for overdue books at 1.00 per day. Track payment status and support partial payments.
- **Reservation System** — Members can reserve books; tracks waiting, completed, and cancelled reservations.
- **Email-Based Authentication** — Custom authentication system using email addresses instead of usernames for easier member management.

## Tech Stack

- **Django** 6.0.4+
- **Python** 3.14+
- **SQLite**

## Quick Start

### Prerequisites
- Python 3.14 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/milanbairagi/library-management-system.git
   cd library-management-system
   ```

2. **Install dependencies using [uv](https://docs.astral.sh/uv/):**
   ```bash
   uv sync
   ```
   
   Alternatively, if you prefer pip:
   ```bash
   pip install "django>=6.0.4"
   ```

3. **Run database migrations:**
   ```bash
   uv run python manage.py migrate
   ```

4. **Create a superuser account (for admin access):**
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Start the development server:**
   ```bash
   uv run python manage.py runserver
   ```

6. **Access the application:**
   - Main application: http://localhost:8000/
   - Django admin panel: http://localhost:8000/admin/
   - Login with your superuser credentials

## Project Structure

```
library-management-system/
├── core/                    # Django project settings and configuration
│   ├── settings.py         # Main Django settings
│   ├── urls.py             # Root URL routing
│   ├── wsgi.py             # WSGI configuration
│   ├── asgi.py             # ASGI configuration
│   └── constants.py        # Project-wide constants
│
├── books/                  # Book catalog management
│   ├── models.py           # Book and BookItem models
│   ├── views.py            # Book-related views
│   ├── admin.py            # Django admin configuration
│   └── migrations/         # Database migrations
│
├── members/                # User authentication and roles
│   ├── models.py           # Member and Librarian models
│   ├── views.py            # Auth views (login, register, dashboard)
│   ├── backends.py         # Custom email-based authentication backend
│   ├── managers.py         # Custom model managers
│   ├── urls.py             # Auth URL routing
│   ├── templates/          # Login, registration, dashboard templates
│   └── migrations/         # Database migrations
│
├── loans/                  # Loan and fine management
│   ├── models.py           # Loan, Fine, and Reservation models
│   ├── services.py         # Business logic for loans and fines
│   ├── views.py            # Loan management views
│   ├── admin.py            # Django admin configuration
│   └── migrations/         # Database migrations
│
├── library/                # Library operations and book search
│   ├── models.py           # Library model
│   ├── views.py            # Library and search views
│   ├── urls.py             # Library URL routing
│   ├── templates/          # Library templates (index, add_book, etc.)
│   └── migrations/         # Database migrations
│
├── templates/              # Global templates
│   ├── base.html           # Base template for all pages
│   └── partials/           # Reusable template components (navbar, etc.)
│
├── manage.py               # Django management script
├── db.sqlite3              # SQLite database (development)
├── pyproject.toml          # Project dependencies and metadata
└── README.md               # This file
```

### Key Directories Explained

- **core/** — Central Django configuration. Defines installed apps, database settings, authentication backends, and URL routing.
- **books/** — Manages book metadata (Book model) and individual physical copies (BookItem model with status tracking).
- **members/** — Handles user authentication, registration, and role-based access (Member vs Librarian). Uses email-based login.
- **loans/** — Core business logic for issuing/returning books, calculating fines, and managing reservations.
- **library/** — Aggregates library-level operations, book search, and inventory views.
