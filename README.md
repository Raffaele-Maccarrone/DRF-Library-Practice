
# DRF Library Service

A RESTful backend API for a library management system, built with **Django REST Framework** and **PostgreSQL**.

This project is part of a technical assessment practice assignment. It aims to replace manual library workflows with an API for managing customers, book inventory, borrowings, notifications, and payments.

No frontend is required. The API can be explored through Django REST Framework's browsable API and Swagger UI.

> **Project Status:** Under active development. The Users Service and Books Service CRUD are implemented. Books permissions are being finalized as part of Task 2.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend Framework | Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
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
- JWT authentication and token refresh
- User profile retrieval and updates
- Custom User management through Django Admin
- Automated tests for authentication, registration, profiles, and admin access

### Books Service

- Complete CRUD operations for books
- Book inventory management
- Hardcover (`HARD`) and softcover (`SOFT`) support
- Daily borrowing fees in USD
- Input validation for book fields
- Book management through Django Admin
- Custom API permissions
- Automated tests for CRUD operations and permissions

### Books Permissions

Book information is publicly accessible, but modifications are restricted to authenticated staff users.

| Operation | Visitor | Regular User | Staff User |
|---|---|---|---|
| List books (GET) | Allowed | Allowed | Allowed |
| Retrieve book (GET) | Allowed | Allowed | Allowed |
| Create book (POST) | Denied | Denied | Allowed |
| Update book (PUT/PATCH) | Denied | Denied | Allowed |
| Delete book (DELETE) | Denied | Denied | Allowed |

**Permission rules:**

- Read operations do not require authentication.
- Write operations require JWT authentication.
- Only users with `is_staff=True` can create, update, or delete books.
- Unauthenticated write requests return `401 Unauthorized` with the current JWT configuration.
- Authenticated users without staff privileges receive `403 Forbidden`.

These rules are implemented through a custom DRF permission class, `IsAdminOrReadOnly`.

### Development Features

- PostgreSQL integration
- Environment variable configuration
- Automated testing with Pytest
- Code coverage reports
- OpenAPI documentation
- Swagger UI
- Git feature branches and Pull Requests

---

## Project Roadmap

The project consists of **15 mandatory coding tasks**. Optional tasks are excluded from the current scope.

| Task | Description | Status |
|---|---|---|
| 1 | Books Service CRUD | Implemented |
| 2 | Books Permissions | In Progress |
| 3 | Users Service CRUD & JWT | Implemented |
| 4 | Borrowing List & Detail | Planned |
| 5 | Create Borrowing | Planned |
| 6 | Borrowing Filtering | Planned |
| 7 | Return Borrowing | Planned |
| 8 | Telegram Borrowing Notifications | Planned |
| 9 | Overdue Borrowing Notifications | Planned |
| 10 | Payments List & Detail | Planned |
| 11 | Stripe Payment Sessions | Planned |
| 12 | Automated Stripe Sessions | Planned |
| 13 | Payment Success & Cancel Endpoints | Planned |
| 14 | Overdue Fine Payments | Planned |
| 15 | Docker Compose Infrastructure | Planned |

---

## Getting Started

### Prerequisites

Make sure the following are installed:

- Python
- PostgreSQL
- Git
- pip

The installation commands below use Windows PowerShell.

### 1. Clone the repository

```powershell
git clone https://github.com/Raffaele-Maccarrone/DRF-Library-Practice.git
cd DRF-Library-Practice
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL user and database.

Using pgAdmin or psql, connect as a PostgreSQL administrator and run:

```sql
CREATE USER library_user
WITH PASSWORD 'your_secure_password';

CREATE DATABASE library_db
OWNER library_user;
```

If the database or user already exists, use the existing configuration.

### 5. Configure environment variables

Create a `.env` file in the project root using `.env.sample` as a reference.

```dotenv
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

**Important:** Never commit `.env` files, passwords, tokens, or API keys to GitHub.

### 6. Apply database migrations

```powershell
python manage.py migrate
```

### 7. Create a superuser

```powershell
python manage.py createsuperuser
```

Enter the email and password for the administrator account.

### 8. Run the development server

```powershell
python manage.py runserver
```

The application will be available at:

http://127.0.0.1:8000/

The Django Admin is available at:

http://127.0.0.1:8000/admin/

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
| POST | `/books/` | Create a book | Staff Only |
| PUT | `/books/{id}/` | Update a book | Staff Only |
| PATCH | `/books/{id}/` | Partially update a book | Staff Only |
| DELETE | `/books/{id}/` | Delete a book | Staff Only |

### Book Model

| Field | Type | Description |
|---|---|---|
| `id` | Integer | Auto-generated identifier |
| `title` | String | Book title |
| `author` | String | Book author |
| `cover` | Enum | `HARD` or `SOFT` |
| `inventory` | Positive Integer | Available copies |
| `daily_fee` | Decimal | Daily borrowing fee in USD |

## Borrowings API

The Borrowings API provides read-only endpoints for retrieving library borrowing records.

### Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/borrowings/` | List all borrowings | Staff only |
| GET | `/borrowings/{id}/` | Retrieve a borrowing by ID | Staff only |

### Borrowing Model

Each borrowing contains:

- `id`: Unique borrowing identifier.
- `borrow_date`: Date when the book was borrowed.
- `expected_return_date`: Expected return date.
- `actual_return_date`: Actual return date, or `null` if not returned.
- `book`: Related book, including its detailed information.
- `user`: ID of the user who borrowed the book.

### Date Validation

The model implements the following validation rules:

- `expected_return_date` cannot be earlier than `borrow_date`.
- `actual_return_date`, when provided, cannot be earlier than `borrow_date`.

These rules are checked through Django's model validation.

### Permissions

For Task 4, borrowing list and detail endpoints are restricted to staff users.

User-specific access and filtering will be implemented in Task 6.

### Tests

Borrowing tests cover:

- Retrieving a borrowing list.
- Retrieving a specific borrowing.
- Validating the expected return date.
- Validating the actual return date.

Run the tests with:

```bash
python -m pytest borrowings/tests.py -v
```

### API Documentation

The borrowing endpoints are documented using drf-spectacular and are available in the Swagger UI.
### Example: Create a Book

**Endpoint:**

```http
POST /books/
```

**Request Body:**

```json
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}
```

**Expected Response:**

```http
201 Created
```

```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}
```

The ID is generated automatically by the database.

Creating, updating, and deleting books requires staff authentication.

---

## Authentication

The API uses JSON Web Token (JWT) authentication through Simple JWT.

### Obtain Access Token

Send a POST request to:

```http
POST /users/token/
```

With the following JSON body:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

A successful response contains:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN",
  "access": "YOUR_ACCESS_TOKEN"
}
```

### Using the Access Token

Protected endpoints require the custom HTTP header:

```http
Authorize: Bearer YOUR_ACCESS_TOKEN
```

The project uses `Authorize` instead of the default `Authorization` header.

### Refresh Access Token

Send a POST request to:

```http
POST /users/token/refresh/
```

With:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN"
}
```

A valid refresh token allows the client to obtain a new access token.

Keep authentication tokens private.

---

## API Documentation

The project uses **drf-spectacular** to generate OpenAPI documentation.

### Swagger UI

http://127.0.0.1:8000/api/docs/

Swagger UI allows developers to:

- Explore available endpoints
- Inspect request and response schemas
- View required parameters
- Test API requests
- Review authentication requirements

### OpenAPI Schema

http://127.0.0.1:8000/api/schema/

Validate the schema with:

```powershell
python manage.py spectacular --validate
```

---

## Testing

Automated tests are implemented using:

- Pytest
- pytest-django
- Django REST Framework APIClient
- pytest-cov

Tests cover user registration, JWT authentication, profile operations, book CRUD functionality, validation, permissions, and Django Admin integration.

### Run All Tests

```powershell
python -m pytest -v
```

### Run Users Service Tests

```powershell
python -m pytest users/tests.py -v
```

### Run Books Service Tests

```powershell
python -m pytest books/tests.py -v
```

### Code Coverage

Measure Books Service coverage:

```powershell
python -m pytest books/tests.py --cov=books --cov-report=term-missing
```

Measure Users Service coverage:

```powershell
python -m pytest users/tests.py --cov=users --cov-report=term-missing
```

Measure overall coverage:

```powershell
python -m pytest --cov=books --cov=users --cov-report=term-missing
```

The assignment requires at least **60% code coverage** for custom functionality.

The `.coveragerc` configuration excludes migrations and test files from coverage calculations.

### PostgreSQL Test Database

Tests use a separate PostgreSQL database, typically named `test_library_db`.

The development database user must have permission to create test databases.

For local development, this permission can be granted by a PostgreSQL administrator:

```sql
ALTER ROLE library_user CREATEDB;
```

This permission should not be granted unnecessarily in production environments.

---

## Development Workflow

The project follows a task-based Git workflow.

Each mandatory coding task is implemented in a dedicated feature branch.

Example:

```text
main
 |
 +-- feature/users-crud
 |
 +-- feature/books-crud
 |
 +-- feature/books-permissions
 |
 +-- feature/borrowings-list-detail
```

### Git Workflow

1. Create a branch for the task.
2. Implement the required functionality.
3. Add or update automated tests.
4. Run tests and verify coverage.
5. Update the documentation.
6. Commit changes in small, logical steps.
7. Open a Pull Request targeting `main`.
8. Review and merge the Pull Request.

### Commit Conventions

The project uses Conventional Commits.

| Prefix | Purpose |
|---|---|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `test:` | Automated tests |
| `docs:` | Documentation |
| `chore:` | Maintenance and configuration |
| `refactor:` | Code improvements without behavior changes |

Example commit messages:

```text
feat: implement book CRUD viewset
test: add book permission tests
docs: document book API endpoints
fix: prevent unauthorized book updates
```

---

## Planned Modules

### Borrowings Service

The borrowing system will support:

- Creating book borrowings
- Tracking expected and actual return dates
- Decreasing inventory when a book is borrowed
- Increasing inventory when a book is returned
- Filtering active and completed borrowings
- Restricting users to their own borrowing records
- Administrator access to all borrowing records

### Notifications Service

Telegram integration will provide:

- Notifications for newly created borrowings
- Notifications for overdue borrowings
- Scheduled overdue checks
- Background task processing

### Payments Service

Stripe integration will support:

- Payment records
- Stripe Checkout Sessions
- Payment status tracking
- Payment success and cancellation endpoints
- Automatic payment creation for borrowings
- Overdue fine calculation

All Stripe development will use test mode without real transactions.

### Infrastructure

Docker Compose will eventually manage the application's supporting services, including:

- Django API
- PostgreSQL
- Redis
- Background task workers and scheduler

---

## Project Status

This project is currently under active development.

The goal is to complete all 15 mandatory tasks from the DRF Library Practice assignment while maintaining clean code, automated tests, API documentation, and a professional Git workflow.

Optional tasks are not included in the current scope.

