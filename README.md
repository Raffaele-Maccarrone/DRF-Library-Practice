
# DRF Library Service

A RESTful API for managing a library system, built with Django REST Framework and PostgreSQL.

The project allows users to register, authenticate, browse books, borrow books, and manage payments.

This project is part of a Django REST Framework coding practice assignment.

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- Pytest
- pytest-django
- pytest-cov
- drf-spectacular (Swagger/OpenAPI)


## Features

### Implemented

**Users Service**
- Custom User model with email authentication
- User registration and profile management
- JWT authentication and token refresh
- Custom Django Admin integration

**Books Service**
- Book CRUD operations
- Book inventory management
- Hardcover and softcover support
- Daily borrowing fee configuration
- Book management through Django Admin
- Admin-only API access (public read access planned for Task 2)

**Development**
- PostgreSQL database
- Automated tests with Pytest
- Code coverage with pytest-cov
- OpenAPI documentation with Swagger UI

### Planned

- Public read access and admin-only write permissions for books
- Book borrowing and return management
- Borrowing filters
- Telegram notifications
- Stripe payment integration
- Overdue fines
- Docker Compose infrastructure


## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
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

Create a PostgreSQL database and user:

- Database: `library_db`
- User: `library_user`

Ensure the database is owned by `library_user`.

### 5. Configure environment variables

Create a `.env` file in the project root using `.env.sample` as a reference.

```dotenv
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

Never commit the `.env` file or real credentials.

### 6. Apply migrations

```powershell
python manage.py migrate
```

### 7. Run the development server

```powershell
python manage.py runserver
```

The API will be available at:

http://127.0.0.1:8000/

## API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users/` | Register a user |
| POST | `/users/token/` | Obtain JWT tokens |
| POST | `/users/token/refresh/` | Refresh access token |
| GET | `/users/me/` | Retrieve current user |
| PUT | `/users/me/` | Update user profile |
| PATCH | `/users/me/` | Partially update profile |


### Books

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books/` | List all books |
| POST | `/books/` | Create a book |
| GET | `/books/{id}/` | Retrieve book details |
| PUT | `/books/{id}/` | Update a book |
| PATCH | `/books/{id}/` | Partially update a book |
| DELETE | `/books/{id}/` | Delete a book |

Currently, all Books endpoints require an authenticated
staff user. Public read access will be implemented in Task 2.

### Book Fields

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Auto-generated identifier |
| title | String | Book title |
| author | String | Book author |
| cover | Enum | HARD or SOFT |
| inventory | Integer | Available copies (>= 0) |
| daily_fee | Decimal | Daily borrowing fee in USD |

### Example: Create a Book

POST `/books/`

```json
{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "cover": "SOFT",
    "inventory": 5,
    "daily_fee": "1.50"
}
```

Expected response: `201 Created`.

Write operations require JWT authentication with staff
permissions.

Authentication header:

```http
Authorize: Bearer YOUR_ACCESS_TOKEN
```


### Authentication

Protected endpoints require JWT authentication.

Use the custom HTTP header:

```http
Authorize: Bearer YOUR_ACCESS_TOKEN
```

## API Documentation

Swagger UI:

http://127.0.0.1:8000/api/docs/

OpenAPI Schema:

http://127.0.0.1:8000/api/schema/

## Running Tests

Run all tests:

```powershell
python -m pytest -v
```

Run Users Service tests:

```powershell
python -m pytest users/tests.py -v
```

Check test coverage:

```powershell
python -m pytest --cov=users --cov-report=term-missing
```
### Books Service Tests

Run Books tests:

```powershell
python -m pytest books/tests.py -v
```

Check Books code coverage:

```powershell
python -m pytest books/tests.py --cov=books --cov-report=term-missing
```

Check overall project coverage:

```powershell
python -m pytest --cov=books --cov=users --cov-report=term-missing
```

The project requires at least 60% test coverage
of custom functionality.

Tests use a separate PostgreSQL test database. The database user must have the permissions needed to create it.

## Development Workflow

Each mandatory task is developed in a separate Git branch and submitted through a Pull Request to `main`.

Commits follow Conventional Commits:

- `feat:` new functionality
- `fix:` bug fixes
- `test:` automated tests
- `docs:` documentation
- `chore:` maintenance and configuration

## Project Status

Under active development.

The project includes 15 mandatory coding tasks. Optional tasks are outside the current scope.
