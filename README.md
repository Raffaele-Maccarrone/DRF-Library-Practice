
Loading older messages…
como fazer

Para documentar o POST /borrowings/ no Swagger, você só precisa adicionar um segundo extend_schema() ao decorator que já criamos.

Abra borrowings/views.py e deixe a parte da BorrowingListView assim:
@extend_schema_view(
    get=extend_schema(
        summary="List borrowings",
        description="Retrieve a list of library borrowings.",
        tags=["Borrowings"],
    ),
    post=extend_schema(
        summary="Create borrowing",
        description=(
            "Create a borrowing for the authenticated user "
            "and decrease book inventory."
        ),
        tags=["Borrowings"],
    ),
)
class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book", "user").all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer

        return BorrowingReadSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]

        return [IsAdminUser()]
Entendendo o que adicionamos

O @extend_schema_view permite documentar diferentes métodos HTTP da mesma view.

Código
	

Função

get=extend_schema(...)
	

Documenta a listagem de empréstimos

post=extend_schema(...)
	

Documenta a criação de empréstimos

summary
	

Define o título exibido no Swagger

description
	

Explica o comportamento do endpoint

tags
	

Agrupa as operações em Borrowings

O drf-spectacular também utiliza nosso get_serializer_class() para identificar que o POST recebe os campos definidos em BorrowingCreateSerializer.
Agora vamos verificar

Execute:

python manage.py spectacular --validate

Depois:

python -m pytest -v

Se tudo passar, faça o commit:

git add borrowings/views.py
git commit -m "docs: document borrowing creation endpoint"

Próximo passo: verificar a cobertura de testes e atualizar o README com o novo endpoint POST /borrowings/.

Antes de finalizar a Task 5, também vamos conferir se a resposta da criação apresenta os dados esperados do empréstimo, além de verificar o código HTTP 201 e a redução do estoque.
proximo

Vamos para o Passo 9 — Verificar a resposta da API e a cobertura dos testes da Task 5.

Já implementamos a criação de empréstimos, a redução do estoque, as permissões e a documentação Swagger. Agora precisamos garantir que a resposta do POST /borrowings/ esteja correta.
1. Melhorar o teste de criação

Abra borrowings/tests.py e encontre:
def test_authenticated_user_can_create_borrowing(
    regular_client, regular_user, book
):

Você já verifica se a resposta é 201, se o empréstimo pertence ao usuário e se o estoque diminuiu.

Agora adicione mais dois asserts, logo após a requisição:
assert response.data["book"] == book.pk
assert response.data["expected_return_date"] == expected_return_date.isoformat()
Por que fazer isso?

Até agora, nosso teste verifica principalmente o que aconteceu no banco de dados.

Esses novos asserts verificam o conteúdo da resposta HTTP.

Com o BorrowingCreateSerializer atual, esperamos algo semelhante a:

{
  "book": 1,
  "expected_return_date": "2026-10-26"
}

Observe que, por enquanto, a resposta não inclui todos os campos do empréstimo, pois estamos utilizando o serializer de criação.
2. Executar os testes

Primeiro, execute o teste que acabamos de modificar:

python -m pytest borrowings/tests.py::test_authenticated_user_can_create_borrowing -v

Depois, execute todos os testes:

python -m pytest -v

Se todos passarem, faça o commit:

git add borrowings/tests.py
git commit -m "test: verify borrowing creation response"

3. Verificar a cobertura

Execute:

python -m pytest --cov=books --cov=users --cov=borrowings --cov-report=term-missing

Como o requisito do projeto é de 60% de cobertura do código personalizado, podemos obter um relatório mais representativo excluindo testes e migrations:

python -m coverage report --omit="*/tests.py,*/migrations/*" --show-missing

Na Task 4, obtivemos 99% no relatório geral, mas ele também incluía os próprios testes. Agora verificaremos a cobertura do código de implementação.
Progresso da Task 5

Etapa
	

Situação

BorrowingCreateSerializer
	

Implementado

Validação de estoque
	

Implementada

Criação com transaction.atomic
	

Implementada

Permissões GET/POST
	

Implementadas

Testes de criação e validação
	

Verificar execução

Swagger
	

Implementado

Cobertura
	

Verificar agora

README e Pull Request
	

Próximos passos

Execute os testes e os comandos de cobertura e me envie o resultado. Se tudo estiver correto, na próxima etapa vou preparar a atualização do README pronta para copiar, seguida do Pull Request da Task 5.
proximo

Vamos para o Passo 10 — Atualizar o README da Task 5: Create Borrowing.

Agora precisamos documentar o endpoint POST /borrowings/, as validações e o funcionamento do estoque.

Como combinamos para este projeto, vou deixar o texto pronto para copiar e colar, sem você precisar escrever a documentação sozinho.
1. Atualizar a seção Borrowings API

Abra o arquivo README.md e substitua a seção ## Borrowings API pelo conteúdo abaixo.

## Borrowings API

The Borrowings API allows authenticated users to borrow available books and staff users to retrieve borrowing records.

### Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/borrowings/` | List all borrowings | Staff only |
| GET | `/borrowings/{id}/` | Retrieve borrowing details | Staff only |
| POST | `/borrowings/` | Create a new borrowing | Authenticated users |

### Borrowing Model

Each borrowing contains:

- `id`: Unique borrowing identifier.
- `borrow_date`: Date when the book was borrowed.
- `expected_return_date`: Expected return date.
- `actual_return_date`: Actual return date, or `null` if not returned.
- `book`: Related book.
- `user`: User responsible for the borrowing.

### Create a Borrowing

**Endpoint:**

```http
POST /borrowings/
```

**Request Body:**

```json
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}
```

**Successful Response:**

```http
201 Created
```

```json
{
  "book": 1,
  "expected_return_date": "2026-11-15"
}
```

The borrowing date and user are automatically assigned by the server.

### Borrowing Creation Rules

- Authentication is required to create a borrowing.
- The selected book must have available inventory.
- The expected return date cannot be earlier than the borrowing date.
- A successful borrowing decreases the book inventory by one.
- Book inventory cannot become negative through the borrowing creation endpoint.
- Borrowing creation and inventory updates occur inside a database transaction.
- PostgreSQL row-level locking protects inventory updates from concurrent borrowing requests.

### Validation

The API returns `400 Bad Request` when:

- The selected book is out of stock.
- The expected return date is invalid.

Unauthenticated borrowing creation requests are rejected.

### Permissions

Borrowing creation is available to authenticated users.

For Tasks 4 and 5, borrowing list and detail endpoints remain restricted to staff users.

User-specific borrowing access and filtering will be implemented in Task 6.

### Automated Tests

Tests cover:

- Successful borrowing creation.
- Automatic assignment of the authenticated user.
- Inventory reduction after borrowing creation.
- Rejection of out-of-stock books.
- Rejection of invalid expected return dates.
- Rejection of unauthenticated borrowing requests.
- Borrowing date and database constraint validation.

Run borrowing tests:

```bash
python -m pytest borrowings/tests.py -v
```

### API Documentation

Borrowing endpoints are documented using drf-spectacular and available through Swagger UI.
2. Atualizar o Project Roadmap

No roadmap, ajuste estas linhas, desde que os testes finais estejam passando:
| 4 | Borrowing List & Detail | Implemented |
| 5 | Create Borrowing | Implemented |
| 6 | Borrowing Filtering | Planned |

Na seção ## Features, acrescente:
### Borrowings Service

- Borrowing model with book and user relationships
- Borrowing list and detail endpoints
- Authenticated borrowing creation
- Automatic user and borrowing date assignment
- Book inventory validation and automatic reduction
- Atomic transactions and row-level locking
- Borrowing date validation and database constraints
- Automated borrowing tests
3. Atualizar os comandos de cobertura

Na seção ## Testing, substitua o comando de cobertura geral por:

python -m pytest --cov=books --cov=users --cov=borrowings --cov-report=term-missing

Isso inclui o aplicativo borrowings na medição.
4. Fazer o commit

Depois de atualizar o README:

git add README.md
git commit -m "docs: document borrowing creation endpoint"

Confira:

git status

Progresso da Task 5

Create Borrowing
Revisão final

     
    Serializer de criação

     
    Validação de estoque e datas

     
    Transação e redução do inventário

     
    Permissões GET e POST

     
    Documentação Swagger

     
    Confirmar testes e cobertura

     
    README e Pull Request

Próximo passo: fazer a verificação final da Task 5 e preparar o Pull Request com título, descrição e checklist em inglês para o GitHub.
Pasted markdown(2).mdDocument
atualize, mas deixe pronto para copiar e colaer
Worked for 4m 43s

Atualizei o README completo com as funcionalidades da Task 5 — Create Borrowing, preservando as seções anteriores do seu projeto.

 README.md atualizado — pronto para copiar

O arquivo já contém todas as seções organizadas, incluindo:

    Tasks 1 a 4 como implementadas e Task 5 em revisão final.

    POST /borrowings/, com exemplos de requisição e resposta.

    Validação de estoque, datas, transaction.atomic() e select_for_update().

    Permissões de livros e empréstimos.

    Testes, comandos de cobertura e próximos módulos.

    Correção do exemplo de criação de livros que estava na seção errada.

Para copiar e colar no PyCharm: abra o arquivo acima, copie todo o conteúdo (Ctrl + A, Ctrl + C) e substitua o conteúdo do seu README.md.

Mantive a Task 5 como In Progress — Final Verification porque ainda não recebi o resultado final de todos os testes. Depois que passarem, podemos alterar para Implemented.
Commit

Após substituir o README:

git add README.md
git commit -m "docs: update README with borrowing creation API"

Depois execute:

python -m pytest -v
python manage.py spectacular --validate
git status

Com essas verificações concluídas, o próximo passo será preparar o Pull Request da Task 5, com título e descrição em inglês prontos para copiar no GitHub.
README_task5_updated.mdDocument
DRF Library Service

A RESTful backend API for a library management system, built with Django REST Framework and PostgreSQL.

This project is part of a technical assessment practice assignment. It aims to replace manual library workflows with an API for managing customers, book inventory, borrowings, notifications, and payments.

No frontend is required. The API can be explored through Django REST Framework's browsable API and Swagger UI.

    Project Status: Under active development. Users Service, Books Service CRUD and permissions, and borrowing list/detail endpoints have been implemented. Task 5 (Create Borrowing) is in final testing and review.

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
    Automated tests for borrowing reads, creation, validation, and permissions

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

The project consists of 15 mandatory coding tasks. Optional tasks are excluded from the current scope.
Task	Description	Status
1	Books Service CRUD	Implemented
2	Books Permissions	Implemented
3	Users Service CRUD & JWT	Implemented
4	Borrowing List & Detail	Implemented
5	Create Borrowing	In Progress — Final Verification
6	Borrowing Filtering	Planned
7	Return Borrowing	Planned
8	Telegram Borrowing Notifications	Planned
9	Overdue Borrowing Notifications	Planned
10	Payments List & Detail	Planned
11	Stripe Payment Sessions	Planned
12	Automated Stripe Sessions	Planned
13	Payment Success & Cancel Endpoints	Planned
14	Overdue Fine Payments	Planned
15	Docker Compose Infrastructure	Planned
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

The Borrowings API supports authenticated borrowing creation and staff-only read operations.
Method	Endpoint	Description	Access
GET	/borrowings/	List all borrowings	Staff Only
GET	/borrowings/{id}/	Retrieve borrowing details	Staff Only
POST	/borrowings/	Create a borrowing	Authenticated
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
Date Validation

The model defines validation rules requiring:

    expected_return_date to be on or after borrow_date.
    actual_return_date, if present, to be on or after borrow_date.

Django's full_clean() invokes these model-level validation rules; save() does not call full_clean() automatically. Database constraints should also be checked through migrations and tests to ensure invalid dates are rejected at the database level.
Permissions and Future Tasks

For Tasks 4 and 5, staff users can list and retrieve all borrowing records. Any authenticated user can create a borrowing for themselves, but unauthenticated users cannot.

Task 6 will add user-specific read access and filtering. Task 7 will implement returning borrowed books and restoring inventory.
Borrowing Tests

The borrowing test suite covers the read endpoints, model date validation, successful creation, inventory updates, out-of-stock rejection, invalid return dates, and authentication requirements.
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

Tests cover user registration, JWT authentication, profile operations, book CRUD, validation, permissions, borrowing read operations, and borrowing creation.
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

The project follows a task-based Git workflow. Each mandatory coding task is implemented in a dedicated feature branch.

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
Borrowings Service — Next Steps

Future tasks will add:

    Filtering active and completed borrowings
    Restricting users to their own borrowing records
    Administrator filtering by user
    Returning books and increasing inventory after a valid return

Notifications Service

Telegram integration will provide:

    Notifications for newly created borrowings
    Notifications for overdue borrowings
    Scheduled overdue checks
    Background task processing

Payments Service

Stripe integration will support:

    Payment records
    Stripe Checkout Sessions
    Payment status tracking
    Payment success and cancellation endpoints
    Automatic payment creation for borrowings
    Overdue fine calculation

All Stripe development will use test mode without real transactions.
Infrastructure

Docker Compose will eventually manage the application's supporting services, including:

    Django API
    PostgreSQL
    Redis
    Background task workers and scheduler

Project Status

This project is under active development. Tasks 1–4 have been implemented, and Task 5 is awaiting final test and coverage verification before its Pull Request is completed.

The goal is to complete all 15 mandatory tasks from the DRF Library Practice assignment while maintaining clean code, automated tests, API documentation, and a professional Git workflow.

Optional tasks are not included in the current scope.
