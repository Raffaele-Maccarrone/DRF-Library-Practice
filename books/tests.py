from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Book


User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admin@example.com",
        password="AdminPassword123!",
    )


@pytest.fixture
def regular_user():
    return User.objects.create_user(
        email="user@example.com",
        password="UserPassword123!",
    )


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def book():
    return Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        cover=Book.CoverType.SOFT,
        inventory=5,
        daily_fee=Decimal("1.50"),
    )


@pytest.fixture
def book_data():
    return {
        "title": "The Pragmatic Programmer",
        "author": "Andrew Hunt",
        "cover": "SOFT",
        "inventory": 10,
        "daily_fee": "2.50",
    }


def test_admin_can_list_books(admin_client, book):
    url = reverse("book-list")

    response = admin_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["title"] == book.title


def test_admin_can_retrieve_book(admin_client, book):
    url = reverse("book-detail", args=[book.id])

    response = admin_client.get(url)

    assert response.status_code == 200
    assert response.data["title"] == book.title
    assert response.data["inventory"] == 5


def test_admin_can_create_book(admin_client, book_data):
    url = reverse("book-list")

    response = admin_client.post(
        url,
        book_data,
        format="json",
    )

    assert response.status_code == 201
    assert Book.objects.count() == 1
    assert response.data["title"] == book_data["title"]

def test_admin_can_update_book(admin_client, book):
    url = reverse("book-detail", args=[book.id])

    data = {
        "title": "Clean Code Updated",
        "author": "Robert C. Martin",
        "cover": "HARD",
        "inventory": 8,
        "daily_fee": "3.00",
    }

    response = admin_client.put(
        url,
        data,
        format="json",
    )

    assert response.status_code == 200

    book.refresh_from_db()

    assert book.title == "Clean Code Updated"
    assert book.cover == "HARD"
    assert book.inventory == 8
    assert book.daily_fee == Decimal("3.00")


def test_admin_can_partially_update_book(admin_client, book):
    url = reverse("book-detail", args=[book.id])

    response = admin_client.patch(
        url,
        {"inventory": 3},
        format="json",
    )

    assert response.status_code == 200

    book.refresh_from_db()

    assert book.inventory == 3
    assert book.title == "Clean Code"


def test_admin_can_delete_book(admin_client, book):
    url = reverse("book-detail", args=[book.id])

    response = admin_client.delete(url)

    assert response.status_code == 204
    assert not Book.objects.filter(id=book.id).exists()


def test_retrieve_nonexistent_book(admin_client):
    url = reverse("book-detail", args=[999999])

    response = admin_client.get(url)

    assert response.status_code == 404

@pytest.mark.parametrize(
    "field,value",
    [
        ("inventory", -5),
        ("daily_fee", "-1.50"),
        ("cover", "INVALID"),
    ],
)
def test_create_book_with_invalid_data(
    admin_client,
    book_data,
    field,
    value,
):
    book_data[field] = value

    response = admin_client.post(
        reverse("book-list"),
        book_data,
        format="json",
    )

    assert response.status_code == 400
    assert field in response.data
    assert Book.objects.count() == 0

def test_unauthenticated_user_cannot_list_books():
    client = APIClient()

    response = client.get(reverse("book-list"))

    assert response.status_code == 401


def test_regular_user_cannot_list_books(regular_user):
    client = APIClient()
    client.force_authenticate(user=regular_user)

    response = client.get(reverse("book-list"))

    assert response.status_code == 403


def test_regular_user_cannot_create_book(
    regular_user,
    book_data,
):
    client = APIClient()
    client.force_authenticate(user=regular_user)

    response = client.post(
        reverse("book-list"),
        book_data,
        format="json",
    )

    assert response.status_code == 403
    assert Book.objects.count() == 0

def test_admin_can_access_book_list(client, admin_user, book):
    client.force_login(admin_user)

    url = reverse("admin:books_book_changelist")
    response = client.get(url)

    assert response.status_code == 200
    assert book in response.context["cl"].result_list

def test_django_admin_can_create_book(client, admin_user):
    client.force_login(admin_user)

    url = reverse("admin:books_book_add")

    data = {
        "title": "Python Crash Course",
        "author": "Eric Matthes",
        "cover": "SOFT",
        "inventory": 10,
        "daily_fee": "2.50",
        "_save": "Save",
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert Book.objects.filter(
        title="Python Crash Course"
    ).exists()

def test_django_admin_can_update_book(client, admin_user, book):
    client.force_login(admin_user)

    url = reverse("admin:books_book_change", args=[book.id])

    data = {
        "title": book.title,
        "author": book.author,
        "cover": book.cover,
        "inventory": 20,
        "daily_fee": "3.50",
        "_save": "Save",
    }

    response = client.post(url, data)

    assert response.status_code == 302

    book.refresh_from_db()

    assert book.inventory == 20
    assert book.daily_fee == Decimal("3.50")

def test_regular_user_cannot_access_book_admin(
    client, regular_user
):
    client.force_login(regular_user)

    url = reverse("admin:books_book_changelist")
    response = client.get(url)

    assert response.status_code == 302
    assert "/admin/login/" in response.url
