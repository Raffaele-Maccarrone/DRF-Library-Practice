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
