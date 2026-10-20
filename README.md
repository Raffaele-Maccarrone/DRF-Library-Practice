DRF Library Service

A REST API for managing a library's books, users, inventory, and borrowings. Built with Django REST Framework and PostgreSQL as a backend learning and portfolio project.

The project follows a selected scope of 8 tasks from an original 15-task practice assignment. It focuses on a complete borrowing workflow, Telegram integration, and scheduled overdue notifications. No frontend is required; the API can be explored using Swagger UI.
Tech Stack
Area	Technology
Language	Python
Backend	Django, Django REST Framework
Database	PostgreSQL
Authentication	Simple JWT
Notifications	Telegram Bot API, Python urllib
API documentation	drf-spectacular, Swagger UI
Testing	Pytest, pytest-django, pytest-cov
Development	Git, GitHub
Features
Users

    Custom user model with email-based authentication.
    User registration and JWT access/refresh tokens.
    Authenticated profile retrieval and updates.
    User management through Django Admin.

Books

    CRUD endpoints for the book catalog.
    Inventory tracking, book cover type (HARD or SOFT), and daily fees.
    Public access to book listings and details.
    Staff-only permissions for creating, updating, and deleting books.

Borrowings

    List and retrieve borrowing records (staff-only).
    Create borrowings as an authenticated user.
    Automatically associate a borrowing with the current user and date.
    Validate book availability and expected return dates.
    Decrease inventory on borrowing creation and restore it on return.
    Prevent duplicate returns and restrict returns to the owner or staff.
    Protect inventory operations with atomic database transactions and PostgreSQL row-level locks.

Telegram Notifications

    Send messages using the Telegram Bot API.
    Configure the bot token and destination chat ID through environment variables.
    Register borrowing notifications using transaction.on_commit() so rolled-back borrowings are not announced.
    Test API requests with mocks, without sending real messages during automated tests.

The messaging service has been tested successfully with Telegram. Final verification of the automatic notification triggered by POST /borrowings/ remains in progress.
Project Roadmap

The project includes 8 selected tasks, retaining their original task numbers.
Task	Description	Status
1	Books CRUD	Implemented
2	Books Permissions	Implemented
3	Users Service and JWT	Implemented
4	Borrowing List & Detail	Implemented
5	Create Borrowing	Implemented
7	Return Borrowing	Implemented; PR status to confirm
8	Telegram Borrowing Notifications	In progress — final verification
9	Scheduled Overdue Notifications	Planned

Out of scope: Task 6 (borrowing list/detail filtering), Tasks 10–14 (payments and Stripe), Task 15 (full Docker Compose setup), and the original optional tasks.

Regular users can create and return their own borrowings, but borrowing list and detail endpoints remain staff-only because Task 6 is not included.
Getting Started
Prerequisites

    Python and pip
    PostgreSQL
    Git

The commands below use Windows PowerShell.
1. Clone the repository
git clone https://github.com/Raffaele-Maccarrone/DRF-Library-Practice.git
cd DRF-Library-Practice
2. Create a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
3. Install dependencies
python -m pip install -r requirements.txt
4. Configure PostgreSQL

Connect to PostgreSQL as an administrator and create the local development user and database:
CREATE USER library_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE library_db OWNER library_user;

Use your existing user or database if they have already been created.
5. Configure environment variables

Create a .env file in the project root, using .env.sample as a reference:
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

Create a Telegram bot through @BotFather, start a conversation with the bot, and configure the destination chat ID. Telegram settings are needed for live notifications.

Security: Keep real credentials in .env only. Never commit .env, API tokens, or passwords. Use placeholders in .env.sample.
6. Apply migrations
python manage.py migrate
7. Create an administrator
python manage.py createsuperuser
8. Run the server
python manage.py runserver

    API: http://127.0.0.1:8000/
    Django Admin: http://127.0.0.1:8000/admin/
    Swagger UI: http://127.0.0.1:8000/api/docs/

API Reference
Users
Method	Endpoint	Description	Access
POST	/users/	Register a user	Public
POST	/users/token/	Obtain JWT tokens	Public
POST	/users/token/refresh/	Refresh an access token	Public
GET	/users/me/	Retrieve own profile	Authenticated
PUT	/users/me/	Update own profile	Authenticated
PATCH	/users/me/	Partially update own profile	Authenticated
Books
Method	Endpoint	Description	Access
GET	/books/	List books	Public
GET	/books/{id}/	Retrieve book details	Public
POST	/books/	Create a book	Staff
PUT	/books/{id}/	Update a book	Staff
PATCH	/books/{id}/	Partially update a book	Staff
DELETE	/books/{id}/	Delete a book	Staff

Example book creation request:
POST /books/
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}
Borrowings
Method	Endpoint	Description	Access
GET	/borrowings/	List all borrowings	Staff
GET	/borrowings/{id}/	Retrieve borrowing details	Staff
POST	/borrowings/	Borrow an available book	Authenticated
POST	/borrowings/{id}/return/	Return a borrowed book	Owner or staff

Create a borrowing
POST /borrowings/
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}

A successful creation returns HTTP 201 Created. The server automatically sets the current user and borrowing date, checks inventory, creates the borrowing, and decreases the book inventory by one.

Return a borrowing
POST /borrowings/1/return/

No request body is required. A successful return responds with HTTP 200 OK:
{
  "detail": "Borrowing returned successfully."
}

Returning a book sets actual_return_date, restores one inventory unit, and rejects duplicate returns. Regular users may return their own borrowings; staff may return any borrowing.
Borrowing Date Rules

    expected_return_date must not precede borrow_date.
    actual_return_date may be null, but when set it must not precede borrow_date.

Model validation is performed through clean()/full_clean(). Database constraints provide additional protection where configured. A plain model save() does not automatically call full_clean().
Authentication

The API uses JWT authentication through Simple JWT. Obtain tokens by posting an email and password to /users/token/:
{
  "email": "user@example.com",
  "password": "your_password"
}

Send the access token in the project's custom Authorize header (not the standard Authorization header):
Authorize: Bearer YOUR_ACCESS_TOKEN

Use POST /users/token/refresh/ with a refresh token to obtain a new access token.
Telegram Integration

After a successful borrowing is committed to the database, the application attempts to send a Telegram notification containing the book title, user email, borrowing date, and expected return date.

Example message:
📚 New Borrowing!
Book: Clean Code
By user: reader@example.com
Borrowing date: 2026-10-20
Expected return: 2026-10-27

The integration is implemented in borrowings/telegram.py. It sends a JSON request to Telegram's sendMessage endpoint through Python's standard-library urllib.

The borrowing serializer uses transaction.on_commit(..., robust=True) to request notification only after a successful database commit. A notification failure does not undo a committed borrowing; the current implementation does not automatically retry failed messages.

Current status: Direct Telegram delivery has been verified. Automatic end-to-end delivery from borrowing creation is pending final manual verification.
API Documentation

The API schema is generated by drf-spectacular.

    Swagger UI: http://127.0.0.1:8000/api/docs/
    OpenAPI schema: http://127.0.0.1:8000/api/schema/

Validate the schema with:
python manage.py spectacular --validate
Testing

The project uses Pytest, pytest-django, pytest-cov, and DRF's APIClient.

Run all tests:
python -m pytest -v

Run tests for individual applications:
python -m pytest users/tests.py -v
python -m pytest books/tests.py -v
python -m pytest borrowings/tests.py -v

Measure coverage:
python -m pytest --cov=books --cov=users --cov=borrowings --cov-report=term-missing

To view coverage without generated migrations and test files:
python -m coverage report --omit="*/tests.py,*/migrations/*" --show-missing

The original assignment specifies a minimum of 60% coverage of custom code. Tests include permissions, data validation, borrowing inventory updates, returns, and mocked Telegram requests.
PostgreSQL Test Database

Django creates a separate test database, typically test_library_db. For local development, a PostgreSQL administrator can grant the application role permission to create test databases:
ALTER ROLE library_user CREATEDB;

Avoid granting unnecessary database-creation privileges in production.
Development Workflow

Each selected task is developed on a separate Git branch and submitted through a Pull Request to main.

    Create a feature branch.
    Implement the task and write relevant tests.
    Run the test suite and validate API documentation.
    Update the README.
    Commit changes in small, focused commits.
    Open, review, and merge a Pull Request.

Example commit messages:
feat: implement borrowing return endpoint
test: cover Telegram notification callbacks
docs: document Telegram integration
Next Step: Task 9

Scheduled Overdue Notifications will detect unreturned borrowings past their expected return date and send Telegram reminders through a scheduled background task (using Django Q or Celery, depending on the final implementation).

Full Docker Compose infrastructure and Stripe payment integrations are outside the selected eight-task scope.

This repository represents a focused portfolio implementation of 8 selected tasks, not completion of all 15 mandatory tasks in the original assignment.
