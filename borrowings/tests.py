from datetime import date
from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing


@pytest.mark.django_db
def test_admin_can_list_borrowings():
    user = get_user_model().objects.create_superuser(
        email="admin@example.com",
        password="TestPassword123!",
    )

    book = Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        cover="SOFT",
        inventory=5,
        daily_fee=Decimal("1.50"),
    )

    borrowing = Borrowing.objects.create(
        borrow_date=date(2026, 10, 18),
        expected_return_date=date(2026, 10, 25),
        actual_return_date=None,
        book=book,
        user=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("borrowing-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == borrowing.pk
    assert response.data[0]["book"]["title"] == book.title

@pytest.mark.django_db
def test_admin_can_retrieve_borrowing():
    user = get_user_model().objects.create_superuser(
        email="admin@example.com",
        password="TestPassword123!",
    )

    book = Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        cover="SOFT",
        inventory=5,
        daily_fee=Decimal("1.50"),
    )

    borrowing = Borrowing.objects.create(
        borrow_date=date(2026, 10, 18),
        expected_return_date=date(2026, 10, 25),
        actual_return_date=None,
        book=book,
        user=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("borrowing-detail", args=[borrowing.pk])
    response = client.get(url)

    assert response.status_code == 200
    assert response.status_code == 200
    assert response.data["id"] == borrowing.pk
    assert response.data["book"]["title"] == book.title
