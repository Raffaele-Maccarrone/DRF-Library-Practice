# DRF Library Service

A RESTful backend API for a library management system, built with **Django REST Framework** and **PostgreSQL**.

This project is based on a technical assessment practice assignment. Its purpose is to practice backend development through user management, book inventory, borrowing workflows, and notifications.

The original assignment contains 15 mandatory coding tasks. This portfolio implementation focuses on **8 selected tasks** and retains their original numbering. No frontend is required; the API can be explored through Swagger UI.

> **Project Status:** Tasks 1–5 and 7 implemented; Task 8 in final verification; Task 9 planned.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend Framework | Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| Notifications | Telegram Bot API (Python `urllib`) |
| Authentication | Simple JWT |
| API Documentation | drf-spectacular (OpenAPI / Swagger UI) |
| Testing | Pytest, pytest-django |
| Code Coverage | pytest-cov |
| Version Control | Git & GitHub |

---

## Features

### Users Service

- Custom User model with email-based authentication
- User registration
- JWT access and refresh tokens
- User profile retrieval and updates
- User management through Django Admin
- Automated tests for registration, authentication, and profiles

### Books Service

- Complete CRUD operations for books
- Public book listing and detail endpoints
- Staff-only create, update, and delete permissions
- Book inventory management
- Hardcover (`HARD`) and softcover (`SOFT`) options
- Daily borrowing fees
- Automated tests for book CRUD and permissions

### Borrowings Service

- Borrowing model linked to books and users
- Staff-only list and detail endpoints
- Borrowing creation for authenticated users
- Automatic assignment of the authenticated user and borrowing date
- Validation of book inventory and expected return dates
- Automatic inventory reduction on successful borrowing creation
- Atomic transactions and PostgreSQL row-level locking to protect inventory updates
- Date validation for expected and actual return dates
- Return endpoint for owners and staff users
- Automatic return date assignment and inventory restoration
- Prevention of duplicate returns
- Owner-only access for regular users on the return endpoint

### Telegram Notifications

- Telegram Bot API integration for borrowing creation notifications
- Bot token and chat ID configured through environment variables
- HTTP requests implemented using Python's standard-library `urllib`
- Notification messages containing book, user, and borrowing dates
- Notifications registered with `transaction.on_commit()` to avoid announcing rolled-back transactions
- Automated API tests using mocks instead of real Telegram requests
- Manual message delivery to Telegram verified; end-to-end automatic delivery should also be checked before merging

### Books Permissions

Book details are publicly accessible. Only authenticated staff users may modify the catalog.

| Operation | Visitor | Regular User | Staff User |
|---|---|---|---|
| List books (GET) | Allowed | Allowed | Allowed |
| Retrieve book (GET) | Allowed | Allowed | Allowed |
| Create book (POST) | Denied | Denied | Allowed |
| Update book (PUT/PATCH) | Denied | Denied | Allowed |
| Delete book (DELETE) | Denied | Denied | Allowed |

These rules are implemented through `IsAdminOrReadOnly`. With the configured JWT authentication, unauthenticated writes return HTTP 401 and authenticated non-staff writes return HTTP 403.

### Development Features

- PostgreSQL integration
- Environment variable configuration
- Automated testing and coverage reporting
- OpenAPI documentation and Swagger UI
- Feature branches and Pull Requests for individual tasks

---

## Project Roadmap

The scope includes **8 selected tasks** from the original practice assignment. Original task numbers are preserved.

| Task | Description | Status |
|---|---|---|
| 1 | Books Service CRUD | Implemented |
| 2 | Books Permissions | Implemented |
| 3 | Users Service CRUD & JWT | Implemented |
| 4 | Borrowing List & Detail | Implemented |
| 5 | Create Borrowing | Implemented |
| 7 | Return Borrowing | Implemented |
| 8 | Telegram Borrowing Notifications | In final verification |
| 9 | Scheduled Overdue Notifications | Planned |

**Out of scope:** Task 6 (borrowing list/detail filtering), Tasks 10–14 (payments and Stripe), Task 15 (full Docker Compose infrastructure), and the original optional tasks.

Because Task 6 is excluded, borrowing **list and detail** endpoints remain staff-only. Regular users can create borrowings; access to the return endpoint is limited to the borrowing owner or staff beginning in Task 7.

---

## Getting Started

### Prerequisites

Make sure the following are installed:

- Python and pip
- PostgreSQL
- Git

The commands below use Windows PowerShell.

### 1. Clone the repository

```powershell
git clone https://github.com/Raffaele-Maccarrone/DRF-Library-Practice.git
cd DRF-Library-Practice
```

### 2. Create a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a development user and database using pgAdmin or `psql`:

```sql
CREATE USER library_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE library_db OWNER library_user;
```

If they already exist, keep your existing configuration.

### 5. Configure environment variables

Create a `.env` file in the project root using `.env.sample` as a reference:

```dotenv
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

**Important:** Never commit `.env`, real passwords, bot tokens, or API keys. Keep only placeholders in `.env.sample`.

### 6. Apply migrations

```powershell
python manage.py migrate
```

### 7. Create a superuser

```powershell
python manage.py createsuperuser
```

### 8. Run the development server

```powershell
python manage.py runserver
```

- API: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/
- Swagger UI: http://127.0.0.1:8000/api/docs/

### 9. Configure Telegram notifications

1. Create a Telegram bot using [@BotFather](https://t.me/BotFather).
2. Send `/start` to your bot in Telegram.
3. Retrieve the destination chat ID with the Telegram Bot API `getUpdates` method.
4. Add the bot token and chat ID to your local `.env` file.
5. Restart the Django process after updating environment variables.

The Telegram integration requires valid credentials for live delivery. Automated tests mock HTTP requests and do not send real messages.

---

## API Reference

### Users Service

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/users/` | Register a user | Public |
| POST | `/users/token/` | Obtain JWT tokens | Public |
| POST | `/users/token/refresh/` | Refresh access token | Public |
| GET | `/users/me/` | Retrieve current user | Authenticated |
| PUT | `/users/me/` | Update user profile | Authenticated |
| PATCH | `/users/me/` | Partially update profile | Authenticated |

### Books Service

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/books/` | List all books | Public |
| GET | `/books/{id}/` | Retrieve book details | Public |
| POST | `/books/` | Create a book | Staff only |
| PUT | `/books/{id}/` | Update a book | Staff only |
| PATCH | `/books/{id}/` | Partially update a book | Staff only |
| DELETE | `/books/{id}/` | Delete a book | Staff only |

### Book Model

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Auto-generated identifier |
| `title` | String | Book title |
| `author` | String | Book author |
| `cover` | Enum | `HARD` or `SOFT` |
| `inventory` | Positive Integer | Available copies |
| `daily_fee` | Decimal | Daily borrowing fee |

### Example: Create a Book

**Endpoint:** `POST /books/` (staff only)

**Request body:**

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}
```

**Successful response:** HTTP 201 Created with the saved book data and generated ID.

### Borrowings Service

| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | `/borrowings/` | List all borrowings | Staff only |
| GET | `/borrowings/{id}/` | Retrieve borrowing details | Staff only |
| POST | `/borrowings/` | Create a borrowing | Authenticated |
| POST | `/borrowings/{id}/return/` | Return a borrowing | Owner or staff |

### Borrowing Model

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Auto-generated identifier |
| `borrow_date` | Date | Date when the book was borrowed |
| `expected_return_date` | Date | Expected return date |
| `actual_return_date` | Date / null | Actual return date, if returned |
| `book` | ForeignKey | Related book |
| `user` | ForeignKey | User who borrowed the book |

### Example: Create a Borrowing

**Endpoint:** `POST /borrowings/` (authenticated)

**Request body:**

```json
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}
```

**Successful response:** HTTP 201 Created.

```json
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}
```

The API assigns `borrow_date` and `user` automatically. The selected book must have inventory greater than zero, and the expected return date must not be earlier than the borrowing date.

Borrowing creation and inventory reduction run in a database transaction using row-level locking. Invalid requests do not consume inventory.

### Borrowing Read Permissions

Borrowing lists and details are restricted to staff users. User-specific list filtering from Task 6 is not part of the selected project scope.

### Example: Return a Borrowing

**Endpoint:** `POST /borrowings/{id}/return/` (borrowing owner or staff)

No request body is required.

**Successful response:** HTTP 200 OK.

```json
{
  "detail": "Borrowing returned successfully."
}
```

On success, the API sets `actual_return_date` and increases the book's inventory by one. Duplicate returns are rejected with HTTP 400. Requests without authentication are rejected; a regular user attempting to access another user's borrowing receives HTTP 404.

The return operation uses `transaction.atomic()` and row-level locking to keep the borrowing record and inventory consistent.

### Telegram Notification on Borrowing Creation

After a successful borrowing transaction is committed, the application attempts to send a Telegram message containing the book title, user email, borrowing date, and expected return date.

Notifications are registered with `transaction.on_commit(..., robust=True)` so rolled-back borrowings do not produce messages. Telegram failures do not roll back an already committed borrowing; synchronous notifications are not guaranteed to be delivered if the process fails after commit.

---

## Authentication

The API uses JSON Web Token (JWT) authentication through Simple JWT.

### Obtain Access Token

Send a POST request to `/users/token/`:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

The response includes `access` and `refresh` tokens.

### Using the Access Token

The project uses a custom HTTP header, **`Authorize`**, instead of the conventional `Authorization` header:

```http
Authorize: Bearer YOUR_ACCESS_TOKEN
```

### Refresh Access Token

Send the refresh token to `POST /users/token/refresh/`:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

Keep access tokens and refresh tokens private.

---

## API Documentation

The project uses **drf-spectacular** to generate OpenAPI documentation.

- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

Validate the schema with:

```powershell
python manage.py spectacular --validate
```

---

## Testing

Automated tests use Pytest, pytest-django, Django REST Framework's `APIClient`, and pytest-cov.

Tests cover user registration and authentication, book CRUD and permissions, borrowing reads, borrowing creation, date validation, and inventory updates.
Return-specific tests also cover inventory restoration, duplicate-return prevention, ownership checks, and unauthenticated requests.
Telegram tests mock HTTP requests and cover message payloads, missing credentials, simulated API failures, and transaction commit/rollback behavior.

### Run All Tests

```powershell
python -m pytest -v
```

### Run Tests by App

```powershell
python -m pytest users/tests.py -v
python -m pytest books/tests.py -v
python -m pytest borrowings/tests.py -v
```

### Code Coverage

```powershell
python -m pytest --cov=users --cov=books --cov=borrowings --cov-report=term-missing
```

The original assignment requires at least **60% code coverage** for custom functionality. Generated migrations and test modules should not be included when evaluating implementation coverage.

### PostgreSQL Test Database

Pytest uses a separate PostgreSQL test database, typically named `test_library_db`. The development database role must be allowed to create test databases.

For local testing, a PostgreSQL administrator can grant this permission:

```sql
ALTER ROLE library_user CREATEDB;
```

This permission is intended for local development and should not be granted unnecessarily in production.

---

## Development Workflow

Each selected task is implemented on a dedicated feature branch with small, logical commits and a Pull Request targeting `main`.

### Feature Branches

```text
main
 |
 +-- feature/users-crud
 +-- feature/books-crud
 +-- feature/books-permissions
 +-- feature/borrowings-list-detail
 +-- feature/borrowings-create
 +-- feature/borrowings-return
 +-- feature/telegram-notifications
```

### Git Workflow

1. Create a feature branch from the latest `main`.
2. Implement the task and add relevant tests.
3. Run tests and verify coverage.
4. Update the documentation.
5. Commit changes in small, logical steps.
6. Open a Pull Request targeting `main`.
7. Review and merge the Pull Request.

### Commit Conventions

The project follows Conventional Commits.

| Prefix | Purpose |
|---|---|
| `feat:` | New functionality |
| `fix:` | Bug fixes |
| `test:` | Automated tests |
| `docs:` | Documentation |
| `chore:` | Configuration and maintenance |
| `refactor:` | Internal improvements without behavior changes |

---

## Remaining Scope

### Scheduled Overdue Notifications — Task 9

- Find borrowings that are overdue and have not been returned
- Send Telegram notifications about overdue books
- Run checks automatically using a scheduled background task

Full Stripe payments and Docker Compose infrastructure are outside the selected eight-task scope.

---

## Project Status

This is a portfolio-oriented Django REST Framework project based on **8 selected tasks** from the original assignment. It prioritizes clean API design, PostgreSQL consistency, practical integrations, automated tests, and clear documentation. The remaining planned functionality is described above.
