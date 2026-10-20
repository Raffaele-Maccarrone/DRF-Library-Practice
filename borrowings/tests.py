import json
from io import BytesIO
from unittest.mock import patch
from datetime import date, timedelta
from django.utils import timezone
from decimal import Decimal

import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError, transaction
from django.test import override_settings


from books.models import Book
from borrowings.models import Borrowing
from borrowings.telegram import send_telegram_message


@pytest.fixture
def admin_user(db):
    return get_user_model().objects.create_superuser(
        email="admin@example.com",
        password="TestPassword123!",
    )

@pytest.fixture
def regular_user(db):
    return get_user_model().objects.create_user(
        email="reader@example.com",
        password="TestPassword123!",
    )

@pytest.fixture
def regular_client(regular_user):
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client

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

@pytest.mark.django_db
def test_authenticated_user_can_create_borrowing(
    regular_client, regular_user, book
):
    expected_return_date = timezone.localdate() + timedelta(days=7)

    data = {
        "book": book.pk,
        "expected_return_date": expected_return_date.isoformat(),
    }

    response = regular_client.post(
        reverse("borrowing-list"),
        data,
        format="json",
    )
    assert response.status_code == 201
    created_borrowing = Borrowing.objects.get(
        book=book,
        user=regular_user,
    )
    assert created_borrowing.user == regular_user
    book.refresh_from_db()
    assert book.inventory == 4
    assert response.data["book"] == book.pk
    assert response.data["expected_return_date"] == expected_return_date.isoformat()

@pytest.mark.django_db
def test_cannot_create_borrowing_when_book_out_of_stock(
    regular_client, regular_user, book
):
    book.inventory = 0
    book.save(update_fields=["inventory"])

    data = {
        "book": book.pk,
        "expected_return_date": (
            timezone.localdate() + timedelta(days=7)
        ).isoformat(),
    }

    response = regular_client.post(
        reverse("borrowing-list"),
        data,
        format="json",
    )
    assert response.status_code == 400
    Borrowing.objects.filter(
        book=book,
        user=regular_user,
    ).exists()
    book.refresh_from_db()
    assert book.inventory == 0

@pytest.mark.django_db
def test_cannot_create_borrowing_with_invalid_return_date(
    regular_client, regular_user, book
):
    invalid_date = timezone.localdate() - timedelta(days=1)

    data = {
        "book": book.pk,
        "expected_return_date": invalid_date.isoformat(),
    }

    response = regular_client.post(
        reverse("borrowing-list"),
        data,
        format="json",
    )
    assert response.status_code == 400
    assert not Borrowing.objects.filter(
        book=book,
        user=regular_user,
    ).exists()

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_borrowing(book):
    client = APIClient()

    data = {
        "book": book.pk,
        "expected_return_date": (
            timezone.localdate() + timedelta(days=7)
        ).isoformat(),
    }

    response = client.post(
        reverse("borrowing-list"),
        data,
        format="json",
    )
    assert response.status_code == 401
    Borrowing.objects.filter(book=book).exists()
    book.refresh_from_db()
    assert book.inventory == 5

@pytest.mark.django_db
def test_admin_can_return_borrowing(admin_client, borrowing):
    original_inventory = borrowing.book.inventory

    url = reverse("borrowing-return", args=[borrowing.pk])

    response = admin_client.post(url)

    borrowing.refresh_from_db()
    borrowing.book.refresh_from_db()
    assert response.status_code == 200
    assert borrowing.book.inventory == original_inventory + 1
    assert borrowing.actual_return_date == timezone.localdate()

@pytest.mark.django_db
def test_cannot_return_borrowing_twice(admin_client, borrowing):
    url = reverse("borrowing-return", args=[borrowing.pk])

    first_response = admin_client.post(url)

    borrowing.refresh_from_db()
    book = borrowing.book
    book.refresh_from_db()

    inventory_after_first_return = book.inventory

    second_response = admin_client.post(url)

    book.refresh_from_db()

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert borrowing.book.inventory == inventory_after_first_return

@pytest.mark.django_db
def test_user_can_return_only_own_borrowing(
    regular_client, regular_user, borrowing
):
    book = borrowing.book
    original_inventory = book.inventory

    url = reverse("borrowing-return", args=[borrowing.pk])

    response = regular_client.post(url)

    borrowing.refresh_from_db()
    book.refresh_from_db()

    assert response.status_code == 404
    assert borrowing.actual_return_date is None
    assert book.inventory == original_inventory

    data = {
        "book": book.pk,
        "expected_return_date": (
            timezone.localdate() + timedelta(days=7)
        ).isoformat(),
    }

    response = regular_client.post(
        reverse("borrowing-list"),
        data,
        format="json",
    )

    assert response.status_code == 201

    own_borrowing = Borrowing.objects.get(
        book=book,
        user=regular_user,
    )

    book.refresh_from_db()
    assert book.inventory == original_inventory - 1

    url = reverse("borrowing-return", args=[own_borrowing.pk])

    response = regular_client.post(url)

    own_borrowing.refresh_from_db()
    book.refresh_from_db()

    assert response.status_code == 200
    assert own_borrowing.actual_return_date == timezone.localdate()
    assert book.inventory == original_inventory

@pytest.mark.django_db
def test_unauthenticated_user_cannot_return_borrowing(borrowing):
    client = APIClient()

    book = borrowing.book
    original_inventory = book.inventory

    url = reverse("borrowing-return", args=[borrowing.pk])

    response = client.post(url)

    borrowing.refresh_from_db()
    book.refresh_from_db()

    assert response.status_code == 401
    assert borrowing.actual_return_date is None
    assert book.inventory == original_inventory

@override_settings(
    TELEGRAM_BOT_TOKEN="fake-test-token",
    TELEGRAM_CHAT_ID="123456789",
)
def test_send_telegram_message():
    fake_response = BytesIO(
        json.dumps({
            "ok": True,
            "result": {"message_id": 123},
        }).encode("utf-8")
    )

    with patch(
        "borrowings.telegram.urlopen",
        return_value=fake_response,
    ) as mock_urlopen:
        result = send_telegram_message("New borrowing created!")
    assert result["message_id"] == 123
    mock_urlopen.assert_called_once()
    request = mock_urlopen.call_args.args[0]

    assert request.get_method() == "POST"
    payload = json.loads(request.data.decode("utf-8"))
    assert payload["chat_id"] == "123456789"
    assert payload["text"] == "New borrowing created!"

@override_settings(
    TELEGRAM_BOT_TOKEN="",
    TELEGRAM_CHAT_ID="",
)
def test_send_telegram_message_without_configuration():
    with patch("borrowings.telegram.urlopen") as mock_urlopen:
        with pytest.raises(
            ValueError,
            match="Telegram configuration is missing."
        ):
            send_telegram_message("Test message")

    mock_urlopen.assert_not_called()

@override_settings(
    TELEGRAM_BOT_TOKEN="fake-test-token",
    TELEGRAM_CHAT_ID="123456789",
)
@override_settings(
    TELEGRAM_BOT_TOKEN="fake-test-token",
    TELEGRAM_CHAT_ID="123456789",
)
def test_send_telegram_message_api_failure():
    fake_response = BytesIO(
        json.dumps({
            "ok": False,
            "description": "Bad Request",
        }).encode("utf-8")
    )
    with patch(
        "borrowings.telegram.urlopen",
        return_value=fake_response,
    ):
        with pytest.raises(RuntimeError):
            send_telegram_message("Test message")
