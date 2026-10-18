from datetime import date
from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError, transaction

from books.models import Book
from borrowings.models import Borrowing


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        email="admin@example.com",
        password="TestPassword123!",
    )

@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

@pytest.fixture
def book(db):
    return Book.objects.create(
        title="Clean Code",
        author="Robert C. Martin",
        cover="SOFT",
        inventory=5,
        daily_fee=Decimal("1.50"),
    )

@pytest.fixture
def borrowing(book, admin_user):
    return Borrowing.objects.create(
        borrow_date=date(2026, 10, 18),
        expected_return_date=date(2026, 10, 25),
        actual_return_date=None,
        book=book,
        user=admin_user,
    )

@pytest.mark.django_db
def test_admin_can_list_borrowings(admin_client, borrowing):
    response = admin_client.get(reverse("borrowing-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == borrowing.pk
    assert response.data[0]["book"]["title"] == borrowing.book.title

@pytest.mark.django_db
def test_admin_can_retrieve_borrowing(admin_client, borrowing):
    url = reverse("borrowing-detail", args=[borrowing.pk])
    response = admin_client.get(url)

    assert response.status_code == 200
    assert response.status_code == 200
    assert response.data["id"] == borrowing.pk
    assert response.data["book"]["title"] == borrowing.book.title

@pytest.mark.django_db
def test_expected_return_date_cannot_be_before_borrow_date(borrowing):
    borrowing.expected_return_date = date(2026, 10, 17)

    with pytest.raises(ValidationError) as exc_info:
        borrowing.full_clean()

    assert "expected_return_date" in exc_info.value.message_dict

def test_actual_return_date_cannot_be_before_borrow_date(borrowing):
    borrowing.actual_return_date = date(2026, 10, 17)
    with pytest.raises(ValidationError) as exc_info:
        borrowing.full_clean()

    assert "actual_return_date" in exc_info.value.message_dict

@pytest.mark.django_db
def test_database_rejects_invalid_expected_return_date(borrowing):
    borrowing.expected_return_date = date(2026, 10, 17)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            borrowing.save()

@pytest.mark.django_db
def test_database_rejects_invalid_actual_return_date(borrowing):
    borrowing.actual_return_date = date(2026, 10, 17)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            borrowing.save()
