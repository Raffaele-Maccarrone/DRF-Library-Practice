from django.urls import path

from users.views import (
    UserRegistrationView,
    UserProfileView,
)

urlpatterns = [
    path("", UserRegistrationView.as_view(), name="user-register"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
