# DRF Library Service

A RESTful backend API for a library management system, built with **Django REST Framework** and **PostgreSQL**.

This project is based on a technical assessment practice assignment. Its purpose is to practice backend development through user management, book inventory, borrowing workflows, and notifications.

The original assignment contains 15 mandatory coding tasks. This portfolio implementation focuses on **8 selected tasks** and retains their original numbering. No frontend is required; the API can be explored through Swagger UI.

> **Project Status:** All 8 selected tasks (1–5 and 7–9) are implemented. The overdue notification job was successfully executed through Django Q2; recurring execution requires a running Q Cluster.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend Framework | Django |
| REST API | Django REST Framework |
| Database | PostgreSQL |
| Notifications | Telegram Bot API (Python `urllib`) |
| Background Scheduling | Django Q2 (PostgreSQL ORM broker) |
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
- Manual Telegram delivery verified; automated message delivery is covered by mocked tests

### Scheduled Overdue Notifications (Django Q2)

- Daily background check for borrowings whose `expected_return_date` is before the current date and whose `actual_return_date` is `NULL`
- One Telegram message per matching overdue borrowing when the task runs
- Related book and user records loaded efficiently with `select_related()`
- Django Q2 with the PostgreSQL ORM broker; no Redis server required
- Reusable management command (`setup_overdue_schedule`) to register the daily schedule
- Daily schedule set for **9:00 AM** in the Django application's configured time zone
- Automated test ensures current, upcoming, and already-returned borrowings are not incorrectly reported as overdue
- Background task successfully executed using a Django Q2 worker; a live scheduled 9:00 AM run has not been separately verified

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
- Database-backed background task scheduling with Django Q2
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
| 8 | Telegram Borrowing Notifications | Implemented |
| 9 | Scheduled Overdue Notifications | Implemented |

**Out of scope:** Task 6 (borrowing list/detail filtering), Tasks 10–14 (payments and Stripe), Task 15 (full Docker Compose infrastructure), and the original optional tasks.

Because Task 6 is excluded, borrowing **list and detail** endpoints remain staff-only. Regular users can create borrowings; access to the return endpoint is limited to the borrowing owner or staff beginning in Task 7.

---

## Getting Started

### Prerequisites

Make sure the following are installed:

- Python and pip (the project has been tested with Python 3.14)
- PostgreSQL
- Git
- Optional for running the background worker on Windows: WSL2 with Ubuntu

The primary application setup and automated testing commands below use Windows PowerShell. The Django Q2 worker can be run in Linux/WSL2.

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

### 10. Register the daily overdue notification schedule

After applying migrations, run:

```powershell
python manage.py setup_overdue_schedule
```

This command creates or updates the `Daily Overdue Notifications` schedule in the database. The schedule calls `borrowings.tasks.notify_overdue_borrowings` daily at **09:00** in the Django application's configured time zone, with unlimited repetitions.

Re-running the setup command updates the existing schedule **and resets its next execution to 9:00 AM the following day**. Run it during initial setup or when intentionally reconfiguring the schedule, not on every application startup.

**Registering a schedule does not execute it.** A Django Q2 cluster must remain running to process scheduled jobs. The cluster uses the configured PostgreSQL database as its ORM broker.

### 11. Run the background worker (Linux / WSL2)

On Linux, activate the project environment, ensure the database and Telegram settings are available, and start the cluster:

```bash
python manage.py qcluster
```

Keep this process running while scheduled notifications are needed. Stop it with `Ctrl + C`.

**Windows development using WSL2:** The Django server and tests can stay on Windows; the Q Cluster runs in Ubuntu (WSL2), because Django Q2's multiprocessing-based worker is not suited to native Windows execution.

1. Open Ubuntu with `wsl -d Ubuntu`, then enter the project directory (Windows drives are mounted under `/mnt/c/`).
2. Install the Linux Python prerequisites, if needed:

   ```bash
   sudo apt update
   sudo apt install -y python3-venv python3-pip python3-dev libpq-dev build-essential
   ```

3. Create and activate a **separate Linux virtual environment** (do not reuse a Windows `venv`):

   ```bash
   python3 -m venv ~/.venvs/drf-library
   source ~/.venvs/drf-library/bin/activate
   python -m pip install -r requirements.txt
   ```

4. If PostgreSQL runs on Windows and WSL2 uses its default NAT networking, set `POSTGRES_HOST` to the Windows host address for this terminal session:

   ```bash
   export POSTGRES_HOST=$(ip route show default | awk '{print $3; exit}')
   ```

   This requires `config/settings.py` to read `POSTGRES_HOST` from the environment. The address may change after restarting WSL2. Other WSL2 networking modes may require a different host address.

5. Confirm database access, and then start the worker:

   ```bash
   python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('PostgreSQL connected')"
   python manage.py qcluster
   ```

If the WSL2 connection times out, inspect the Windows firewall and PostgreSQL `listen_addresses`. If PostgreSQL reports **no `pg_hba.conf` entry**, add a narrowly scoped `host` rule for the WSL2 IP, the `library_db` database, and the `library_user` role (for example, `host library_db library_user <WSL_IP>/32 scram-sha-256`), then reload PostgreSQL's configuration. Avoid opening database access to all network addresses.

When finished, first stop `qcluster` with `Ctrl + C`. In Windows PowerShell, shut down only Ubuntu with:

```powershell
wsl --terminate Ubuntu
```

Use `wsl --list --verbose` to confirm its status is `Stopped`. Stopping WSL2 also stops the background worker, so no scheduled notifications will run while Ubuntu is off.

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

### Telegram Notifications for Overdue Borrowings

The background function `borrowings.tasks.notify_overdue_borrowings` selects borrowings satisfying both conditions:

- `expected_return_date < timezone.localdate()`
- `actual_return_date IS NULL`

For each matching borrowing, it sends a Telegram message containing the book title, borrower email, and expected return date. The scheduled job checks daily; an overdue borrowing may produce a reminder on each day it remains unreturned. This is a **background job**, not an additional HTTP API endpoint.

The Django Q2 setup command registers the recurring schedule, while a running Q Cluster dispatches it. See [Getting Started](#10-register-the-daily-overdue-notification-schedule) for setup instructions.

For a **manual live run**, keep `qcluster` running in one terminal, open another terminal connected to the same database, and run:

```python
from django_q.tasks import async_task, fetch

task_id = async_task("borrowings.tasks.notify_overdue_borrowings")
task = fetch(task_id, wait=5000)
print(task.success, task.result) if task is not None else print("Pending")
```

Execute this from `python manage.py shell`. **This can send real Telegram notifications** when overdue borrowings exist; do not enqueue the task repeatedly just to check whether it finished. A successful manual run has been verified; an unattended daily 9:00 AM execution has not been separately observed.

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
The overdue notification test uses mocks and covers overdue, not-yet-due, and already-returned borrowings without making real Telegram requests.

**Latest verified test run (Windows, Python 3.14.5 / Django 6.1.2): 52 tests passed, 98% reported total coverage.** The reported total includes tests and migrations; it is not a production-code-only coverage figure. The scheduling management command was not exercised by the test suite (0% for that file), although the command was used to configure the schedule during manual development.

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
 +-- feature/overdue-notifications
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

## Scope and Limitations

- All eight selected tasks are implemented; original task numbering is retained.
- Task 6 (user-filtered borrowing list/detail), Stripe payments, and full Docker Compose infrastructure are intentionally out of scope.
- The overdue job may send repeated daily reminders until a borrowing is returned; reminder deduplication and retry policies are not part of this implementation.
- The job runs only while the Django Q2 cluster is active. A successful manual queue execution was verified, but the unattended scheduled run has not been independently observed.
- Borrowing-creation Telegram notifications are dispatched after database commit, but delivery is best-effort and does not have a persistent retry queue.

---

## Project Status

This is a portfolio-oriented Django REST Framework project implementing **8 selected tasks** from the original assignment. It demonstrates JWT authentication, permissions, transactional inventory management, borrowing returns, Telegram integration, and database-backed scheduled notifications.

**Verification:** 52 automated tests passed on Windows, with 98% reported overall coverage (including tests and migrations). The Django Q2 background function also completed successfully through a running Linux/WSL2 cluster. Daily execution requires keeping that cluster available.
