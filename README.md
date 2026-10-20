Loading older messages…
proximo

Vamos continuar a Task 7 — Return Borrowing!

Agora estamos no Passo 11 — Testar devoluções sem autenticação.

Já criamos testes para verificar se o usuário consegue devolver o próprio livro, não consegue devolver o de outra pessoa e não consegue devolver o mesmo empréstimo duas vezes.

Falta verificar se um visitante sem autenticação pode acessar o endpoint de devolução.
1. Comportamento esperado

Verificação
	

Resultado

POST /borrowings/{id}/return/ sem autenticação
	

HTTP 401

actual_return_date
	

Continua None

Estoque do livro
	

Não é alterado
2. Criar o teste

Abra borrowings/tests.py e adicione:
@pytest.mark.django_db
def test_unauthenticated_user_cannot_return_borrowing(borrowing):
    client = APIClient()

    book = borrowing.book
    original_inventory = book.inventory

    url = reverse("borrowing-return", args=[borrowing.pk])

    response = client.post(url)

    borrowing.refresh_from_db()
    book.refresh_from_db()

    # Seus asserts aqui

Observe que utilizamos APIClient() sem force_authenticate(), pois queremos simular um visitante.
3. Seu desafio

Complete os três asserts para verificar que:

    response.status_code é 401.

    borrowing.actual_return_date continua None.

    book.inventory continua igual a original_inventory.

Você já utilizou essas verificações nos testes anteriores.
4. Executar o teste

Primeiro, execute somente o novo teste:

python -m pytest borrowings/tests.py::test_unauthenticated_user_cannot_return_borrowing -v

Depois, execute todos os testes de Borrowings:

python -m pytest borrowings/tests.py -v

Se todos passarem, registre os testes de devolução:

git add borrowings/tests.py
git commit -m "test: cover borrowing returns and permissions"

Sua tarefa agora: complete os três asserts e me envie o resultado. Depois vamos documentar o endpoint no Swagger e finalizar a Task 7.
proximo

Vamos continuar a Task 7 — Return Borrowing!

Agora estamos no Passo 12 — Documentar a devolução no Swagger.

Já implementamos a lógica de devolução e escrevemos os testes principais. Vamos documentar o endpoint:
POST /borrowings/{id}/return/
1. Adicionar a documentação

Abra borrowings/views.py.

Confira se você possui estas importações:
from drf_spectacular.utils import extend_schema, OpenApiResponse

Agora, dentro de BorrowingReturnView, coloque este decorator imediatamente acima do método post():
@extend_schema(
    summary="Return borrowing",
    description=(
        "Return a borrowed book and increase its inventory by one. "
        "Users can return their own borrowings, while staff "
        "members can return any borrowing."
    ),
    request=None,
    responses={
        200: OpenApiResponse(description="Borrowing returned successfully."),
        400: OpenApiResponse(description="Borrowing already returned."),
        401: OpenApiResponse(description="Authentication required."),
        404: OpenApiResponse(description="Borrowing not found or not accessible."),
    },
    tags=["Borrowings"],
)
def post(self, request, pk):
    # Mantenha aqui a implementação que já fizemos.
O que há de novo?

    request=None: indica que a requisição não precisa receber dados no corpo. O ID do empréstimo já vem da URL.

    responses: documenta os possíveis códigos HTTP retornados pela API.

    OpenApiResponse: permite descrever cada resposta.

Não precisa modificar a lógica do método post().
2. Verificar no Swagger

Execute:

python manage.py spectacular --validate

Depois abra o Swagger com o servidor em execução:

http://127.0.0.1:8000/api/docs/

Na seção Borrowings, você deverá encontrar:

Método
	

Endpoint
	

Descrição

GET
	

/borrowings/
	

List borrowings

POST
	

/borrowings/
	

Create borrowing

GET
	

/borrowings/{id}/
	

Retrieve borrowing

POST
	

/borrowings/{id}/return/
	

Return borrowing
3. Executar todos os testes

python -m pytest borrowings/tests.py -v

Depois:

python -m pytest -v

Se tudo passar, podemos preparar os commits da Task 7.
Próximo passo

Vamos revisar o código da devolução, conferir a cobertura e atualizar o README.

Por enquanto, adicione o decorator e execute a validação do Swagger. Se aparecer algum warning ou erro, envie a mensagem para corrigirmos antes de fazer o commit.
proximo

Vamos para o Passo 13 — Revisão final e cobertura de testes da Task 7 — Return Borrowing.

Agora que implementamos o endpoint, as permissões, os testes e a documentação Swagger, precisamos verificar se está tudo funcionando antes dos commits e do Pull Request.
1. Revisar a BorrowingReturnView

Abra borrowings/views.py.

Confira se sua implementação atende a estas condições:

    Usa IsAuthenticated para impedir devoluções sem login.

    Usa get_queryset() para permitir que usuários comuns acessem apenas os próprios empréstimos.

    Utiliza transaction.atomic() e select_for_update() para proteger a operação.

    Impede uma segunda devolução quando actual_return_date is not None.

    Registra a data atual e aumenta o estoque exatamente uma vez.

    Salva os dois objetos no banco de dados.

A parte de atualização deve estar assim:
borrowing.actual_return_date = timezone.localdate()
borrowing.save(update_fields=["actual_return_date"])

book.inventory += 1
book.save(update_fields=["inventory"])

O retorno HTTP 200 deve acontecer depois da conclusão da transação.
2. Executar os testes

Primeiro, execute todos os testes de Borrowings:

python -m pytest borrowings/tests.py -v

Depois, a suíte completa:

python -m pytest -v

Se algum teste falhar, vamos corrigir antes de continuar.
3. Verificar a cobertura

Execute:

python -m pytest --cov=books --cov=users --cov=borrowings --cov-report=term-missing

Para conferir a cobertura sem incluir testes e migrations:

python -m coverage report --omit="*/tests.py,*/migrations/*" --show-missing

Lembre-se: nosso requisito é de pelo menos 60% de cobertura do código personalizado, não necessariamente 100%.
4. Preparar os commits

Se os testes passaram e você ainda não registrou as alterações da Task 7, podemos criar dois commits separados:

Implementação:

git add borrowings/views.py borrowings/urls.py
git commit -m "feat: implement borrowing return endpoint"

Testes:

git add borrowings/tests.py
git commit -m "test: cover borrowing returns and permissions"

Se já fez algum desses commits, não precisa repetir.
Progresso da Task 7

Return Borrowing

6/8
Endpoint de devolução
Atualização da data e do estoque
Proteção contra devolução duplicada
Permissões por proprietário
Testes automatizados
Documentação Swagger
Verificação final dos testes
README e Pull Request

Agora execute os testes e me envie o resultado da cobertura. Depois vamos atualizar o README completo, pronto para copiar e colar, e preparar o Pull Request da Task 7.

Após isso, começaremos a Task 8 — Telegram Notifications, nossa primeira integração com uma API externa.
atualizer o readme tambem com o novo objetivo de 8 tasks
Worked for 2m 56s

Atualizei o README completo com nosso novo objetivo de 8 tasks, incluindo a Task 7 — Return Borrowing.

README atualizado — 8 Tasks

Markdown completo, pronto para copiar e colar no PyCharm.

 Baixar README atualizado
Novo planejamento no README

Task
	

Funcionalidade
	

Status

1–5
	

Funcionalidades já desenvolvidas
	

Concluídas

7
	

Return Borrowing
	

Revisão final

8
	

Telegram Notifications
	

Pendente

9
	

Overdue Notifications
	

Pendente

Também atualizei a documentação da devolução, as permissões, os testes e as próximas etapas. As Tasks 6 e 10–15 agora aparecem como fora do escopo, e removi pagamentos e Docker Compose do planejamento ativo.

Mantive a Task 7 em revisão final porque ainda precisamos confirmar os testes e o Pull Request.
Como aplicar

Abra o arquivo acima, copie todo o conteúdo e substitua seu README.md no PyCharm.

Depois, execute:

git add README.md
git commit -m "docs: update README for eight-task project scope and returns"

Próximo passo: finalizar o Pull Request da Task 7 e começar nossa primeira integração externa na Task 8 — Telegram Notifications.
DRF Library Service

A RESTful backend API for a library management system, built with Django REST Framework and PostgreSQL.

This project is based on a technical assessment practice assignment. It replaces manual library workflows with an API for managing users, books, inventory, borrowings, returns, and notifications.

Current scope: 8 selected tasks from the original 15-task assignment. This is a focused learning and portfolio implementation, not a claim that all mandatory tasks in the original assignment are complete.

No frontend is required. The API can be explored through Django REST Framework's browsable API and Swagger UI.

    Project Status: Under active development. Tasks 1–5 are implemented. Task 7 (Return Borrowing) is under final testing and review. Tasks 8 (Telegram Notifications) and 9 (Overdue Notifications) are planned.

Tech Stack
Category	Technology
Language	Python
Backend Framework	Django
REST API	Django REST Framework
Database	PostgreSQL
Authentication	Simple JWT
API Documentation	drf-spectacular (OpenAPI / Swagger UI)
Testing	Pytest, pytest-django
Code Coverage	pytest-cov
Version Control	Git & GitHub
Features
Users Service

    Custom User model with email-based authentication
    User registration
    JWT authentication and token refresh
    User profile retrieval and updates
    Custom User management through Django Admin
    Automated tests for authentication, registration, profiles, and admin access

Books Service

    Complete CRUD operations for books
    Book inventory management
    Hardcover (HARD) and softcover (SOFT) support
    Daily borrowing fees in USD
    Input validation for book fields
    Book management through Django Admin
    Custom API permissions
    Automated tests for CRUD operations and permissions

Borrowings Service

    Borrowing records linked to books and users
    Borrowing list and detail endpoints
    Borrowing creation for authenticated users
    Automatic assignment of the borrowing date and authenticated user
    Book availability validation before creating a borrowing
    Automatic inventory decrement after a successful borrowing
    Atomic borrowing creation and inventory update
    PostgreSQL row-level locking during inventory updates
    Expected and actual return date validation
    Return endpoint to record a return and restore one inventory unit (Task 7: in final review)
    Prevention of duplicate returns and restriction of returns to the borrowing owner or staff
    Automated tests for borrowing reads, creation, returns, validation, and permissions

Books Permissions

Book information is publicly accessible, but modifications are restricted to authenticated staff users.
Operation	Visitor	Regular User	Staff User
List books (GET)	Allowed	Allowed	Allowed
Retrieve book (GET)	Allowed	Allowed	Allowed
Create book (POST)	Denied	Denied	Allowed
Update book (PUT/PATCH)	Denied	Denied	Allowed
Delete book (DELETE)	Denied	Denied	Allowed

Permission rules:

    Read operations do not require authentication.
    Write operations require JWT authentication.
    Only users with is_staff=True can create, update, or delete books.
    Unauthenticated write requests return 401 Unauthorized with the current JWT configuration.
    Authenticated users without staff privileges receive 403 Forbidden.

These rules are implemented through a custom DRF permission class, IsAdminOrReadOnly.
Development Features

    PostgreSQL integration
    Environment variable configuration
    Automated testing with Pytest
    Code coverage reports
    OpenAPI documentation and Swagger UI
    Git feature branches and Pull Requests

Project Roadmap

The original practice assignment contains 15 mandatory coding tasks. For this focused portfolio project, the development goal has been reduced to 8 selected tasks. The original task numbers are retained for traceability.
Original Task	Description	Status
1	Books Service CRUD	Implemented
2	Books Permissions	Implemented
3	Users Service CRUD & JWT	Implemented
4	Borrowing List & Detail	Implemented
5	Create Borrowing	Implemented
7	Return Borrowing	In Progress — Final Review
8	Telegram Borrowing Notifications	Planned
9	Overdue Borrowing Notifications	Planned

Progress: 5 of 8 tasks implemented; Task 7 is undergoing final testing and documentation. Tasks 8 and 9 have not been implemented yet.

Out of scope: Task 6 (Borrowing Filtering), Tasks 10–14 (Payments/Stripe), and Task 15 (Docker Compose). Optional assignment tasks are also excluded. The absence of Task 6 means full user-specific read/list filtering is not implemented; borrowing list/detail reads remain staff-only. Return-specific ownership checks are being implemented in Task 7.
Getting Started
Prerequisites

Make sure the following are installed:

    Python
    PostgreSQL
    Git
    pip

The installation commands below use Windows PowerShell.
1. Clone the repository
git clone https://github.com/Raffaele-Maccarrone/DRF-Library-Practice.git
cd DRF-Library-Practice
2. Create a virtual environment
python -m venv venv

Activate the environment:
.\venv\Scripts\Activate.ps1
3. Install dependencies
python -m pip install -r requirements.txt
4. Configure PostgreSQL

Create a PostgreSQL user and database. Using pgAdmin or psql, connect as a PostgreSQL administrator and run:
CREATE USER library_user
WITH PASSWORD 'your_secure_password';

CREATE DATABASE library_db
OWNER library_user;

If the database or user already exists, use the existing configuration.
5. Configure environment variables

Create a .env file in the project root using .env.sample as a reference.
POSTGRES_DB=library_db
POSTGRES_USER=library_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

Important: Never commit .env files, passwords, tokens, or API keys to GitHub.
6. Apply database migrations
python manage.py migrate
7. Create a superuser
python manage.py createsuperuser

Enter the email and password for the administrator account.
8. Run the development server
python manage.py runserver

Application: http://127.0.0.1:8000/

Django Admin: http://127.0.0.1:8000/admin/

Swagger UI: http://127.0.0.1:8000/api/docs/
API Reference
Users Service
Method	Endpoint	Description	Access
POST	/users/	Register a user	Public
POST	/users/token/	Obtain JWT tokens	Public
POST	/users/token/refresh/	Refresh access token	Public
GET	/users/me/	Retrieve current user	Authenticated
PUT	/users/me/	Update user profile	Authenticated
PATCH	/users/me/	Partially update profile	Authenticated
Books Service
Method	Endpoint	Description	Access
GET	/books/	List all books	Public
GET	/books/{id}/	Retrieve book details	Public
POST	/books/	Create a book	Staff Only
PUT	/books/{id}/	Update a book	Staff Only
PATCH	/books/{id}/	Partially update a book	Staff Only
DELETE	/books/{id}/	Delete a book	Staff Only
Book Model
Field	Type	Description
id	Integer	Auto-generated identifier
title	String	Book title
author	String	Book author
cover	Enum	HARD or SOFT
inventory	Positive Integer	Available copies
daily_fee	Decimal	Daily borrowing fee in USD
Example: Create a Book

Endpoint:
POST /books/

Request body:
{
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}

Successful response: 201 Created
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "cover": "SOFT",
  "inventory": 5,
  "daily_fee": "1.50"
}

The ID is generated automatically by the database. Creating, updating, and deleting books requires staff authentication.
Borrowings Service

The Borrowings API supports authenticated borrowing creation and staff-only list/detail operations. Task 7 adds a return action for the borrowing owner or staff; that action is currently under final review.
Method	Endpoint	Description	Access
GET	/borrowings/	List all borrowings	Staff Only
GET	/borrowings/{id}/	Retrieve borrowing details	Staff Only
POST	/borrowings/	Create a borrowing	Authenticated
POST	/borrowings/{id}/return/	Return a borrowing (Task 7 — final review)	Borrowing owner or staff
Borrowing Model

Each borrowing contains:

    id: Unique borrowing identifier.
    borrow_date: Date when the book was borrowed.
    expected_return_date: Expected return date.
    actual_return_date: Actual return date, or null if the book has not been returned.
    book: Related book. Read responses include nested book details.
    user: User responsible for the borrowing.

Create a Borrowing

Endpoint:
POST /borrowings/

Required authentication header:
Authorize: Bearer YOUR_ACCESS_TOKEN

Request body:
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}

Successful response: 201 Created
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}

The BorrowingCreateSerializer accepts only book and expected_return_date. The authenticated user and current borrowing date are assigned automatically by the server. The creation response contains the fields exposed by that serializer.
Borrowing Creation Rules

    Authentication is required to create a borrowing.
    The book must have at least one available copy (inventory > 0).
    expected_return_date cannot be earlier than the borrowing date.
    A successful request creates a borrowing and decreases the book inventory by one.
    Creation and inventory updates are performed within transaction.atomic().
    The book record is locked with select_for_update() and its stock is checked again before creating the borrowing. This protects against concurrent requests borrowing the last available copy on PostgreSQL.
    If the transaction fails and the exception leaves the atomic block, its database changes are rolled back.

Validation errors return 400 Bad Request, such as when a book has no inventory or the expected return date is invalid. Requests without valid authentication are rejected.
Return a Borrowing (Task 7 — In Progress)

Endpoint:
POST /borrowings/1/return/

This operation requires JWT authentication. No request body is required.

Expected successful response: 200 OK
{
  "detail": "Borrowing returned successfully."
}

The return workflow is designed to:

    Set actual_return_date to the current date.
    Increase the associated book's inventory by exactly one.
    Reject a second return of the same borrowing with 400 Bad Request.
    Permit staff to return any borrowing and regular users to return only their own; attempts to access another user's borrowing return 404 Not Found.
    Reject unauthenticated requests (normally 401 Unauthorized with the configured JWT authentication).
    Use transaction.atomic() and row-level locking so that recording the return and updating inventory form one transaction, including protection against duplicate concurrent returns.

Status: Implemented in the development branch; final tests, schema validation, and PR verification are pending. This endpoint should not be treated as released until the branch is merged.
Date Validation

The model defines validation rules requiring:

    expected_return_date to be on or after borrow_date.
    actual_return_date, if present, to be on or after borrow_date.

Django's full_clean() invokes these model-level validation rules; save() does not call full_clean() automatically. Database constraints should also be checked through migrations and tests to ensure invalid dates are rejected at the database level.
Permissions and Scope

    GET /borrowings/ and GET /borrowings/{id}/ are staff-only.
    Any authenticated user can create a borrowing for themselves with POST /borrowings/.
    The Task 7 return action allows a user to return their own borrowing or staff to return any borrowing; it is under final review.
    Task 6 (list/detail filtering for regular users) has been intentionally excluded. Regular users do not receive general read access to their borrowing lists or details in the selected scope.

Borrowing Tests

The borrowing test suite covers read endpoints, model date validation, successful creation, inventory updates, out-of-stock rejection, invalid return dates, and authentication requirements. Task 7 adds tests for successful returns, duplicate-return prevention, ownership restrictions, and unauthenticated requests. Final test results for Task 7 still need confirmation.
python -m pytest borrowings/tests.py -v

Borrowing endpoints are documented with drf-spectacular and available in Swagger UI.
Authentication

The API uses JSON Web Token (JWT) authentication through Simple JWT.
Obtain Access Token

Send a POST request to:
POST /users/token/

With the following JSON body:
{
  "email": "user@example.com",
  "password": "your_password"
}

A successful response contains:
{
  "refresh": "YOUR_REFRESH_TOKEN",
  "access": "YOUR_ACCESS_TOKEN"
}
Using the Access Token

Protected endpoints require the custom HTTP header:
Authorize: Bearer YOUR_ACCESS_TOKEN

The project uses Authorize instead of the default Authorization header.
Refresh Access Token

Send a POST request to:
POST /users/token/refresh/

With:
{
  "refresh": "YOUR_REFRESH_TOKEN"
}

A valid refresh token allows the client to obtain a new access token. Keep authentication tokens private.
API Documentation

The project uses drf-spectacular to generate OpenAPI documentation.
Swagger UI

http://127.0.0.1:8000/api/docs/

Swagger UI allows developers to explore available endpoints, inspect schemas, view parameters, test API requests, and review authentication requirements.
OpenAPI Schema

http://127.0.0.1:8000/api/schema/

Validate the schema with:
python manage.py spectacular --validate
Testing

Automated tests use Pytest, pytest-django, Django REST Framework APIClient, and pytest-cov.

Tests cover user registration, JWT authentication, profile operations, book CRUD, validation, permissions, and borrowing read/creation operations. Return-action tests are being finalized as part of Task 7.
Run All Tests
python -m pytest -v
Run Individual App Tests
python -m pytest users/tests.py -v
python -m pytest books/tests.py -v
python -m pytest borrowings/tests.py -v
Code Coverage

Measure overall coverage across the three applications:
python -m pytest --cov=books --cov=users --cov=borrowings --cov-report=term-missing

For a report excluding test files and migrations:
python -m coverage report --omit="*/tests.py,*/migrations/*" --show-missing

The assignment requires at least 60% code coverage for custom functionality. Coverage should be evaluated on application code, rather than using test files and generated migrations to inflate the percentage.
PostgreSQL Test Database

Tests use a separate PostgreSQL database, typically named test_library_db.

The development database user must have permission to create test databases. For local development, this permission can be granted by a PostgreSQL administrator:
ALTER ROLE library_user CREATEDB;

This permission should not be granted unnecessarily in production environments.
Development Workflow

The project follows a task-based Git workflow. Each selected task is implemented in a dedicated feature branch and Pull Request.

Example:
main
 |
 +-- feature/users-crud
 |
 +-- feature/books-crud
 |
 +-- feature/books-permissions
 |
 +-- feature/borrowings-list-detail
 |
 +-- feature/borrowings-create
 |
 +-- feature/borrowings-return
Git Workflow

    Create a branch for the task.
    Implement the required functionality.
    Add or update automated tests.
    Run tests and verify coverage.
    Update the documentation.
    Commit changes in small, logical steps.
    Open a Pull Request targeting main.
    Review and merge the Pull Request.

Commit Conventions

The project uses Conventional Commits.
Prefix	Purpose
feat:	New features
fix:	Bug fixes
test:	Automated tests
docs:	Documentation
chore:	Maintenance and configuration
refactor:	Code improvements without behavior changes

Example commit messages:
feat: implement book CRUD viewset
test: add book permission tests
docs: document borrowing creation endpoint
fix: prevent unauthorized book updates
Planned Modules
Task 8 — Telegram Borrowing Notifications

The next integration will send a Telegram message when a borrowing is created. Implementation will include:

    Telegram bot configuration and API integration.
    Secure storage of bot credentials in environment variables; .env.sample will document required keys without containing secrets.
    Error handling and automated tests for notifications.

Status: Planned; not yet available in the API.
Task 9 — Scheduled Overdue Notifications

The final selected task will detect overdue, unreturned borrowings and send reminders using Telegram. Implementation will include:

    A daily scheduled check for borrowings past expected_return_date with no actual_return_date.
    Background job processing using Django Q or Celery, as chosen during implementation.
    Integration with the Telegram notification logic from Task 8.
    Tests for due-date conditions, scheduling logic, and duplicate-message handling as appropriate.

Status: Planned; background workers and any required supporting infrastructure are not configured yet. Task 15's full Docker Compose environment is outside the selected scope; only infrastructure essential to run the scheduled task will be added.
Scope Exclusions

The current eight-task roadmap does not include:

    Task 6: User-facing borrowing list/detail filtering.
    Tasks 10–14: Payments, Stripe Checkout, payment status, or overdue fines.
    Task 15: Full Docker Compose infrastructure.

This is a deliberate reduction of the original assignment's scope. It prioritizes a complete borrow/return workflow, an external messaging integration, and scheduled backend jobs.
Project Status

This project is under active development with a revised goal of eight selected tasks from the original 15-task practice assignment.

    Implemented: Tasks 1, 2, 3, 4, and 5 (books, permissions, users/JWT, borrowing reads, borrowing creation).
    Under final review: Task 7 (return borrowing, restore inventory, return-specific ownership checks, and tests).
    Planned: Task 8 (Telegram notifications) and Task 9 (scheduled overdue notifications).

The project is intended as a focused Python/Django REST Framework portfolio project, with PostgreSQL, JWT authentication, tests, OpenAPI documentation, and task-based Git history. Completing the eight selected tasks does not constitute completing all mandatory tasks of the original assignment.
