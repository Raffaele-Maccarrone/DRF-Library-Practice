import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
    )


@pytest.mark.django_db
def test_register_user(api_client):
    url = reverse("user-register")

    data = {
        "email": "new@example.com",
        "password": "TestPassword123!",
        "first_name": "New",
        "last_name": "User",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 201
    assert response.data["email"] == data["email"]
    assert "password" not in response.data

    user = User.objects.get(email=data["email"])
    assert user.check_password(data["password"])


@pytest.mark.django_db
def test_register_duplicate_email(api_client, user):
    url = reverse("user-register")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "password": "AnotherPassword123!",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_without_email(api_client):
    url = reverse("user-register")

    response = api_client.post(
        url,
        {"password": "TestPassword123!"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_obtain_jwt_token(api_client, user):
    url = reverse("token-obtain-pair")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_invalid_jwt_credentials(api_client, user):
    url = reverse("token-obtain-pair")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "password": "WrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_refresh_jwt_token(api_client, user):
    login_response = api_client.post(
        reverse("token-obtain-pair"),
        {
            "email": user.email,
            "password": "TestPassword123!",
        },
        format="json",
    )

    assert login_response.status_code == 200

    refresh_token = login_response.data["refresh"]

    response = api_client.post(
        reverse("token-refresh"),
        {"refresh": refresh_token},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_profile(api_client):
    url = reverse("user-profile")

    response = api_client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_user_can_access_profile(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("user-profile"))

    assert response.status_code == 200
    assert response.data["email"] == user.email


@pytest.mark.django_db
def test_update_user_profile(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("user-profile"),
        {"first_name": "Updated"},
        format="json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.first_name == "Updated"


@pytest.mark.django_db
def test_user_cannot_change_staff_permission(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.patch(
        reverse("user-profile"),
        {"is_staff": True},
        format="json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.is_staff is False
